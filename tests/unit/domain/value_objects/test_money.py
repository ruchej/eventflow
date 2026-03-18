"""Тесты для Value Object Money."""

from decimal import Decimal

import pytest

from src.domain.value_objects import Money


class TestMoney:
    """Набор тестов для проверки Money."""

    @pytest.mark.parametrize(
        "amount,currency",
        [
            (Decimal("100.50"), "RUB"),
            (Decimal("0.01"), "USD"),
            (Decimal("999999.99"), "EUR"),
            (Decimal("1"), "GBP"),
            (Decimal("500"), "CNY"),
        ],
    )
    def test_create_valid_money(self, amount, currency):
        """Создание валидного Money."""
        money = Money(amount, currency)
        assert money.amount == amount
        assert money.currency == currency

    @pytest.mark.parametrize(
        "amount",
        [
            Decimal("-1"),
            Decimal("-100.50"),
            Decimal("-0.01"),
        ],
    )
    def test_create_money_non_positive_amount_raises_error(self, amount):
        """Попытка создать Money с неположительной суммой."""
        with pytest.raises(ValueError, match="положительным"):
            Money(amount, "RUB")

    @pytest.mark.parametrize(
        "currency",
        [
            "rub",  # Нижний регистр
            "Rub",  # Смешанный
            "rUb",  # Смешанный
        ],
    )
    def test_create_money_lowercase_currency_raises_error(self, currency):
        """Попытка создать Money с валютой не в верхнем регистре."""
        with pytest.raises(ValueError, match="верхнем регистре"):
            Money(Decimal("100"), currency)

    @pytest.mark.parametrize(
        "currency",
        [
            "R",  # 1 символ
            "RU",  # 2 символа
            "RUBU",  # 4 символа
            "RUBLES",  # 6 символов
        ],
    )
    def test_create_money_invalid_currency_length_raises_error(self, currency):
        """Попытка создать Money с неверной длиной валюты."""
        with pytest.raises(ValueError, match="три буквы"):
            Money(Decimal("100"), currency)

    @pytest.mark.parametrize(
        "currency",
        [
            "R1B",  # Цифры
            "123",  # Только цифры
            "RU$",  # Спецсимвол
            "R_B",  # Подчёркивание
            "R B",  # Пробел
        ],
    )
    def test_create_money_non_alpha_currency_raises_error(self, currency):
        """Попытка создать Money с не-буквами в валюте."""
        with pytest.raises(ValueError, match="только буквы"):
            Money(Decimal("100"), currency)

    def test_money_is_immutable(self):
        """Проверка неизменяемости Money."""
        money = Money(Decimal("100"), "RUB")
        with pytest.raises(AttributeError):
            money.amount = Decimal("200")  # noqa
