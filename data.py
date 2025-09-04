from decimal import Decimal
from typing import Optional

class DataProgram:
    _balance: Decimal = Decimal("1000.00")

    @classmethod
    def execute(cls, operation: str, balance: Optional[Decimal] = None) -> Decimal:
        if operation.upper() == "READ":
            return cls._read()
        elif operation.upper() == "WRITE":
            if balance is None:
                raise ValueError("Balance required for WRITE operation")
            return cls._write(balance)
        else:
            raise ValueError(f"Invalid operation: {operation}")

    @classmethod
    def _read(cls) -> Decimal:
        return cls._balance

    @classmethod
    def _write(cls, balance: Decimal) -> Decimal:
        if balance < Decimal("0"):
            raise ValueError("Balance cannot be negative")
        cls._balance = balance
        return cls._balance

    @classmethod
    def reset(cls) -> None:
        cls._balance = Decimal("1000.00")