from decimal import Decimal, InvalidOperation
from typing import Optional
from data import DataProgram

class Operations:
    @classmethod
    def execute(cls, operation: str) -> None:
        operation_upper = operation.upper()
        if operation_upper == "TOTAL":
            cls._view_balance()
        elif operation_upper == "CREDIT":
            cls._credit_account()
        elif operation_upper == "DEBIT":
            cls._debit_account()
        else:
            print(f"Invalid operation: {operation}")

    @classmethod
    def _view_balance(cls) -> None:
        balance = DataProgram.execute("READ")
        print(f"Current balance: {balance:.2f}")

    @classmethod
    def _credit_account(cls) -> None:
        amount = cls._get_amount("credit")
        if amount is None:
            return
        if amount <= Decimal("0"):
            print("Invalid amount. Please try again.")
            return
        current_balance = DataProgram.execute("READ")
        new_balance = current_balance + amount
        DataProgram.execute("WRITE", new_balance)
        print(f"Amount credited. New balance: {new_balance:.2f}")

    @classmethod
    def _debit_account(cls) -> None:
        amount = cls._get_amount("debit")
        if amount is None:
            return
        if amount <= Decimal("0"):
            print("Invalid amount. Please try again.")
            return
        current_balance = DataProgram.execute("READ")
        if amount > current_balance:
            print("Insufficient funds for this debit.")
            return
        new_balance = current_balance - amount
        DataProgram.execute("WRITE", new_balance)
        print(f"Amount debited. New balance: {new_balance:.2f}")

    @classmethod
    def _get_amount(cls, operation_type: str) -> Optional[Decimal]:
        try:
            amount_str = input(f"Enter {operation_type} amount: ")
            return Decimal(amount_str.strip())
        except (InvalidOperation, ValueError, EOFError):
            print("Invalid amount format.")
            return None
        except KeyboardInterrupt:
            raise