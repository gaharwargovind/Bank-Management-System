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