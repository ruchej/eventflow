from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Денежная сумма с валютой.

    Value Object для представления денег в бизнес-логике.
    Сумма всегда положительная, валюта — 3 заглавные буквы (ISO 4217).

    Attributes:
        amount: Положительная сумма денег (Decimal)
        currency: Код валюты в верхнем регистре (RUB, USD, EUR)

    Example:
        >>> money = Money(Decimal("100.50"), "RUB")
        >>> money.amount
        Decimal('100.50')

        >>> Money(Decimal("-10"), "RUB")  # ValueError
        >>> Money(Decimal("10"), "rub")   # ValueError
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Количество денег должно быть положительным числом")
        if not self.currency.isalpha():
            raise ValueError("Валюта должна содержать только буквы")
        if not self.currency.isupper():
            raise ValueError("Валюта должна быть в верхнем регистре")
        if len(self.currency) != 3:
            raise ValueError("Обозначение валюты должно содержать три буквы")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Нельзя сложить {self.currency} и {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)
