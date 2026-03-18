"""Тесты для EventStatsEntity."""

from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.entities import EventStatsEntity
from src.domain.value_objects import EventType, Money, TimeRange


class TestEventStatsEntity:
    """Набор тестов для проверки EventStatsEntity."""

    @pytest.mark.parametrize(
        "total_money",
        [
            None,
            Money(Decimal("100"), "RUB"),
        ],
        ids=[
            "without money",
            "with money",
        ],
    )
    def test_create_valid_event_stats(
        self,
        total_money: Money | None,
    ):
        """Создание валидного EventStats."""
        stats = EventStatsEntity(
            time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
            total_events=0,
            by_type={
                EventType.PURCHASE: 0,
                EventType.CLICK: 0,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
            total_money=total_money,
        )
        assert stats.total_money == total_money

    @pytest.mark.parametrize(
        "total_events",
        [
            0,
            1,
            100,
            1000000,
        ],
        ids=[
            "zero events",
            "one event",
            "hundred events",
            "million events",
        ],
    )
    def test_create_event_stats_valid_total_events(self, total_events: int):
        """Создание EventStats с валидным количеством событий."""
        stats = EventStatsEntity(
            time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
            total_events=total_events,
            by_type={
                EventType.PURCHASE: 0,
                EventType.CLICK: 0,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
        )
        assert stats.total_events == total_events

    @pytest.mark.parametrize(
        "total_events",
        [
            -1,
            -10,
            -100,
        ],
        ids=[
            "negative one",
            "negative ten",
            "negative hundred",
        ],
    )
    def test_create_event_stats_negative_total_events_raises_error(
        self, total_events: int
    ):
        """Попытка создать EventStats с отрицательным total_events."""
        with pytest.raises(ValueError, match="total_events"):
            EventStatsEntity(
                time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
                total_events=total_events,
                by_type={
                    EventType.PURCHASE: 0,
                    EventType.CLICK: 0,
                    EventType.VIEW: 0,
                    EventType.REGISTRATION: 0,
                },
            )

    @pytest.mark.parametrize(
        "by_type",
        [
            {
                EventType.PURCHASE: 5,
                EventType.CLICK: 10,
                EventType.VIEW: 20,
                EventType.REGISTRATION: 3,
            },
            {
                EventType.PURCHASE: 0,
                EventType.CLICK: 0,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
        ],
        ids=[
            "with events distribution",
            "all zeros",
        ],
    )
    def test_create_event_stats_valid_by_type(self, by_type: dict[EventType, int]):
        """Создание EventStats с валидным распределением по типам."""
        stats = EventStatsEntity(
            time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
            total_events=sum(by_type.values()),
            by_type=by_type,
        )
        assert stats.by_type == by_type

    @pytest.mark.parametrize(
        "by_type",
        [
            {
                EventType.PURCHASE: -1,
                EventType.CLICK: 0,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
            {
                EventType.PURCHASE: 5,
                EventType.CLICK: -10,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
            {
                EventType.PURCHASE: 0,
                EventType.CLICK: 0,
                EventType.VIEW: -5,
                EventType.REGISTRATION: 0,
            },
        ],
        ids=[
            "negative PURCHASE",
            "negative CLICK",
            "negative VIEW",
        ],
    )
    def test_create_event_stats_negative_by_type_raises_error(
        self, by_type: dict[EventType, int]
    ):
        """Попытка создать EventStats с отрицательным значением в by_type."""
        with pytest.raises(ValueError, match="типам"):
            EventStatsEntity(
                time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
                total_events=10,  # Валидное значение
                by_type=by_type,
            )

    @pytest.mark.parametrize(
        "amount,currency",
        [
            (Decimal("0"), "RUB"),
            (Decimal("-1"), "RUB"),
            (Decimal("-100.50"), "RUB"),
        ],
        ids=[
            "zero money",
            "negative money",
            "negative money with decimals",
        ],
    )
    def test_create_event_stats_non_positive_total_money_raises_error(
        self, amount: Decimal, currency: str
    ):
        """Попытка создать EventStats с неположительной total_money."""
        with pytest.raises(ValueError, match="денег"):
            EventStatsEntity(
                time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
                total_events=10,
                by_type={
                    EventType.PURCHASE: 10,
                    EventType.CLICK: 0,
                    EventType.VIEW: 0,
                    EventType.REGISTRATION: 0,
                },
                total_money=Money(amount, currency),
            )

    def test_event_stats_is_immutable(self):
        """Проверка неизменяемости EventStatsEntity."""
        stats = EventStatsEntity(
            time_range=TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31)),
            total_events=10,
            by_type={
                EventType.PURCHASE: 5,
                EventType.CLICK: 5,
                EventType.VIEW: 0,
                EventType.REGISTRATION: 0,
            },
            total_money=Money(Decimal("100"), "RUB"),
        )
        with pytest.raises(AttributeError):
            stats.total_events = 20
