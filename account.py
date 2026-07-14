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