from bank import Bank
from account import SavingsAccount
from acc_menu import MENU

class InvalidPinError(Exception):
    pass

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