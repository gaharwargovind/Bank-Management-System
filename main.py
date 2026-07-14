from datetime import datetime
import hashlib

class InsufficientFundsError(Exception):
    pass


class InvalidAmountError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class InvalidPinError(Exception):
    pass


class Account:
    def __init__(
        self,
        account_no: str,
        account_name: str,
        pin,
        balance: float = 0.0,
        is_hashed: bool = False,
    ):
        self.account_no = str(account_no)
        self.account_name = account_name
        self._balance = balance

        if is_hashed:
            self.__pin = pin
        else:
            self.__pin = hashlib.sha256(
                str(pin).encode()
            ).hexdigest()

        self.transactions = []
        self.log(
            f"Account created for {self.account_name}"
        )
    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):

        if value < 0:
            raise ValueError(
                "Balance cannot be negative."
            )

        self._balance = value


    def deposit(self, amount: float):

        if amount <= 0:
            raise InvalidAmountError(
                "Deposit amount must be greater than zero."
            )

        self.balance += amount

        self.log(
            f"Deposited ₹{amount:.2f}"
        )


    def withdraw(self, amount: float):

        if amount <= 0:
            raise InvalidAmountError(
                "Withdrawal amount must be greater than zero."
            )

        if amount > self.balance:
            raise InsufficientFundsError(
                "Insufficient balance."
            )

        self.balance -= amount

        self.log(
            f"Withdrawn ₹{amount:.2f}"
        )

    def show_balance(self):

        return (
            f"Account Number : {self.account_no}\n"
            f"Balance        : ₹{self.balance:.2f}"
        )

    def log(self, message):

        timestamp = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        self.transactions.append(
            f"[{timestamp}] {message}"
        )

    def account_type(self):

        raise NotImplementedError(
            "Subclass must implement account_type()."
        )

    def display_details(self):

        history = (
            "\n".join(self.transactions)
            if self.transactions
            else "No Transactions"
        )

        return (
            f"\n"
            f"Account Number : {self.account_no}\n"
            f"Account Holder : {self.account_name}\n"
            f"Account Type   : {self.account_type()}\n"
            f"Balance        : ₹{self.balance:.2f}\n"
            f"\nTransaction History\n"
            f"{'-'*30}\n"
            f"{history}"
        )
    def verify_pin(self, pin):

        hashed = hashlib.sha256(
            str(pin).encode()
        ).hexdigest()

        return hashed == self.__pin


    def to_dict(self):

        data = {
            "account_no": self.account_no,
            "account_name": self.account_name,
            "pin": self.__pin,
            "balance": self.balance,
            "transactions": self.transactions,
            "account_type": self.account_type(),
        }

        data.update(
            self._extra_fields()
        )

        return data

    def _extra_fields(self):
        return {}

class SavingsAccount(Account):

    MIN_BALANCE = 500
    DEFAULT_INTEREST = 4.0

    def __init__(
        self,
        account_no,
        account_name,
        pin,
        balance=500,
        interest_rate=DEFAULT_INTEREST,
        is_hashed=False,
    ):

        super().__init__(
            account_no,
            account_name,
            pin,
            balance,
            is_hashed,
        )

        self.interest_rate = interest_rate

    def account_type(self):

        return "Savings Account"

    def withdraw(self, amount):

        if amount <= 0:
            raise InvalidAmountError(
                "Withdrawal amount must be positive."
            )

        if (
            self.balance - amount
            < self.MIN_BALANCE
        ):
            raise InsufficientFundsError(
                f"Minimum balance of ₹{self.MIN_BALANCE:.2f} must be maintained."
            )

        self.balance -= amount

        self.log(
            f"Withdrawn ₹{amount:.2f}"
        )

    def apply_interest(self):

        interest = (
            self.balance
            * self.interest_rate
            / 100
        )

        self.balance += interest

        self.log(
            f"Interest Credited ₹{interest:.2f}"
        )

        return interest

    def _extra_fields(self):

        return {
            "interest_rate": self.interest_rate
        }

class CurrentAccount(Account):

    def __init__(
        self,
        account_no,
        account_name,
        pin,
        balance=0,
        overdraft_limit=1000,
        is_hashed=False,
    ):

        self.overdraft_limit = overdraft_limit

        super().__init__(
            account_no,
            account_name,
            pin,
            balance,
            is_hashed,
        )

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):

        if value < -self.overdraft_limit:
            raise InsufficientFundsError(
                f"Overdraft limit of ₹{self.overdraft_limit:.2f} exceeded."
            )

        self._balance = value

    def account_type(self):

        return "Current Account"

    def withdraw(self, amount):

        if amount <= 0:
            raise InvalidAmountError(
                "Withdrawal amount must be positive."
            )

        self.balance -= amount

        self.log(
            f"Withdrawn ₹{amount:.2f}"
        )

    def _extra_fields(self):

        return {
            "overdraft_limit": self.overdraft_limit
        }

import json
import os


class Bank:
    DATA_FILE = "bank_data.json"

    def __init__(self, name="Everyone's Bank"):
        self.name = name
        self.accounts = {}
        self.next_number = 1001
        self.load_data()

    def create_account(
        self,
        account_name,
        pin,
        acc_type="savings",
        initial_deposit=0.0,
    ):

        acc_number = str(self.next_number)
        self.next_number += 1

        acc_type = acc_type.lower().strip()

        if acc_type == "savings":

            if initial_deposit < SavingsAccount.MIN_BALANCE:
                raise ValueError(
                    f"Minimum opening balance for Savings Account is ₹{SavingsAccount.MIN_BALANCE:.2f}"
                )

            account = SavingsAccount(
                acc_number,
                account_name,
                pin,
                initial_deposit,
            )

        elif acc_type == "current":

            account = CurrentAccount(
                acc_number,
                account_name,
                pin,
                initial_deposit,
            )

        else:
            raise ValueError(
                "Account type must be savings or current."
            )

        self.accounts[acc_number] = account

        self.save_data()

        print("\nAccount Created Successfully")
        print(f"Account Number : {acc_number}")

        return account

    def find_account(self, acc_number):

        acc_number = str(acc_number)

        if acc_number not in self.accounts:
            raise AccountNotFoundError(
                "Account not found."
            )

        return self.accounts[acc_number]

    def deposit(self, acc_number, amount):

        account = self.find_account(acc_number)

        account.deposit(amount)

        self.save_data()

        print(f"\nDeposit Successful")
        print(f"Current Balance : ₹{account.balance:.2f}")

    def withdraw(self, acc_number, amount):

        account = self.find_account(acc_number)

        account.withdraw(amount)

        self.save_data()

        print(f"\nWithdrawal Successful")
        print(f"Current Balance : ₹{account.balance:.2f}")

    def transfer(
        self,
        from_acc,
        to_acc,
        amount,
    ):

        if from_acc == to_acc:
            raise ValueError(
                "Cannot transfer to same account."
            )

        sender = self.find_account(from_acc)

        receiver = self.find_account(to_acc)

        sender.withdraw(amount)

        receiver.deposit(amount)

        sender.log(
            f"Transferred ₹{amount:.2f} to Account {to_acc}"
        )

        receiver.log(
            f"Received ₹{amount:.2f} from Account {from_acc}"
        )

        self.save_data()

        print("\nTransfer Successful")

    def show_all_accounts(self):

        if not self.accounts:
            print("No accounts available.")
            return

        for account in self.accounts.values():

            print(account.display_details())

            print("-" * 50)

    def save_data(self):

        data = {
            "next_number": self.next_number,
            "accounts": [
                account.to_dict()
                for account in self.accounts.values()
            ],
        }

        with open(
            self.DATA_FILE,
            "w",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )

    def load_data(self):

        if not os.path.exists(self.DATA_FILE):
            return

        with open(
            self.DATA_FILE,
            "r",
        ) as file:

            data = json.load(file)

        self.next_number = data.get(
            "next_number",
            1001,
        )

        for acc_data in data.get(
            "accounts",
            [],
        ):

            if (
                acc_data["account_type"]
                == "Savings Account"
            ):

                account = SavingsAccount(
                    acc_data["account_no"],
                    acc_data["account_name"],
                    acc_data["pin"],
                    acc_data["balance"],
                    acc_data.get(
                        "interest_rate",
                        4.0,
                    ),
                    True,
                )

            else:

                account = CurrentAccount(
                    acc_data["account_no"],
                    acc_data["account_name"],
                    acc_data["pin"],
                    acc_data["balance"],
                    acc_data.get(
                        "overdraft_limit",
                        1000,
                    ),
                    True,
                )

            account.transactions = acc_data.get(
                "transactions",
                [],
            )

            self.accounts[
                account.account_no
            ] = account

def main():

    bank = Bank("Gaharwar National Bank")

    MENU = """
========== GAHARWAR NATIONAL BANK ==========

1. Create Account
2. Deposit
3. Withdraw
4. Transfer
5. View All Accounts
6. Apply Interest
7. Check Balance
8. Exit
"""

    print(f"\nWelcome to {bank.name}!")

    while True:

        print(MENU)

        choice = input("Enter your choice: ").strip()

        try:

            if choice == "1":

                name = input("Enter Account Holder Name: ").strip()

                pin = input("Create 4-digit PIN: ").strip()

                if not (pin.isdigit() and len(pin) == 4):
                    raise InvalidPinError(
                        "PIN must be exactly 4 digits."
                    )

                acc_type = input(
                    "Account Type (Savings/Current): "
                ).strip().lower()

                amount = float(
                    input("Initial Deposit: ₹")
                )

                bank.create_account(
                    name,
                    int(pin),
                    acc_type,
                    amount,
                )

            elif choice == "2":

                acc_no = input("Account Number: ").strip()

                amount = float(
                    input("Deposit Amount: ₹")
                )

                bank.deposit(
                    acc_no,
                    amount,
                )

            elif choice == "3":

                acc_no = input("Account Number: ").strip()

                account = bank.find_account(acc_no)

                pin = input("Enter PIN: ").strip()

                if not account.verify_pin(pin):
                    raise InvalidPinError(
                        "Incorrect PIN."
                    )

                amount = float(
                    input("Withdrawal Amount: ₹")
                )

                bank.withdraw(
                    acc_no,
                    amount,
                )

            elif choice == "4":

                from_acc = input(
                    "Sender Account Number: "
                ).strip()

                sender = bank.find_account(from_acc)

                pin = input(
                    "Enter Sender PIN: "
                ).strip()

                if not sender.verify_pin(pin):
                    raise InvalidPinError(
                        "Incorrect PIN."
                    )

                to_acc = input(
                    "Receiver Account Number: "
                ).strip()

                amount = float(
                    input("Transfer Amount: ₹")
                )

                bank.transfer(
                    from_acc,
                    to_acc,
                    amount,
                )

            elif choice == "5":

                bank.show_all_accounts()

            elif choice == "6":

                acc_no = input(
                    "Savings Account Number: "
                ).strip()

                account = bank.find_account(acc_no)

                if not isinstance(
                    account,
                    SavingsAccount,
                ):
                    raise ValueError(
                        "Interest can only be applied to Savings Accounts."
                    )

                interest = account.apply_interest()

                bank.save_data()

                print(
                    f"Interest Credited : ₹{interest:.2f}"
                )

                print(
                    f"Current Balance : ₹{account.balance:.2f}"
                )

            elif choice == "7":

                acc_no = input(
                    "Account Number: "
                ).strip()

                account = bank.find_account(acc_no)

                pin = input(
                    "Enter PIN: "
                ).strip()

                if not account.verify_pin(pin):
                    raise InvalidPinError(
                        "Incorrect PIN."
                    )

                print()

                print(account.show_balance())

            elif choice == "8":

                bank.save_data()

                print(
                    "\nThank you for using Gaharwar National Bank."
                )

                break

            else:

                print(
                    "Invalid Choice. Please try again."
                )

        except (
            InvalidAmountError,
            InsufficientFundsError,
            AccountNotFoundError,
            InvalidPinError,
            ValueError,
        ) as e:

            print(f"\nError: {e}")

        except Exception as e:

            print(f"\nUnexpected Error: {e}")


if __name__ == "__main__":
    main()