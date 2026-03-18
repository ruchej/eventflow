"""Тесты для Domain Service: EventAggregator."""

from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.entities import EventEntity
from src.domain.services import EventAggregator
from src.domain.value_objects import EventType, Money, TimeRange, UserId


class TestEventAggregator:
    """Набор тестов для проверки EventAggregator."""

    @pytest.fixture
    def aggregator(self) -> EventAggregator:
        """Создание агрегатора."""
        return EventAggregator()

    def test_aggregate_empty_events_list(self, aggregator: EventAggregator):
        """Агрегация пустого списка событий."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))

        stats = aggregator.aggregate([], time_range)

        assert stats.total_events == 0
        assert stats.by_type == {}
        assert stats.total_money is None
        assert stats.time_range == time_range

    def test_aggregate_single_purchase_event(self, aggregator: EventAggregator):
        """Агрегация одного PURCHASE события."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 15),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 1
        assert stats.by_type == {EventType.PURCHASE: 1}
        assert stats.total_money == Money(Decimal("100"), "RUB")

    def test_aggregate_single_click_event(self, aggregator: EventAggregator):
        """Агрегация одного CLICK события (без money)."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.CLICK,
                money=None,
                timestamp=datetime(2026, 1, 15),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 1
        assert stats.by_type == {EventType.CLICK: 1}
        assert stats.total_money is None

    def test_aggregate_multiple_events_different_types(
        self, aggregator: EventAggregator
    ):
        """Агрегация нескольких событий разных типов."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 10),
            ),
            EventEntity(
                id="evt_002",
                user_id=UserId("usr_1"),
                event_type=EventType.CLICK,
                money=None,
                timestamp=datetime(2026, 1, 15),
            ),
            EventEntity(
                id="evt_003",
                user_id=UserId("usr_1"),
                event_type=EventType.VIEW,
                money=None,
                timestamp=datetime(2026, 1, 20),
            ),
            EventEntity(
                id="evt_004",
                user_id=UserId("usr_1"),
                event_type=EventType.REGISTRATION,
                money=None,
                timestamp=datetime(2026, 1, 25),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 4
        assert stats.by_type == {
            EventType.PURCHASE: 1,
            EventType.CLICK: 1,
            EventType.VIEW: 1,
            EventType.REGISTRATION: 1,
        }
        assert stats.total_money == Money(Decimal("100"), "RUB")

    def test_aggregate_multiple_purchases_sum_money(self, aggregator: EventAggregator):
        """Агрегация нескольких PURCHASE: сумма money считается корректно."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 10),
            ),
            EventEntity(
                id="evt_002",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("50.50"), "RUB"),
                timestamp=datetime(2026, 1, 15),
            ),
            EventEntity(
                id="evt_003",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("200"), "RUB"),
                timestamp=datetime(2026, 1, 20),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 3
        assert stats.by_type == {EventType.PURCHASE: 3}
        assert stats.total_money == Money(Decimal("350.50"), "RUB")

    def test_aggregate_filter_events_by_time_range(self, aggregator: EventAggregator):
        """Агрегация: события вне time_range не учитываются."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            # В диапазоне
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 15),
            ),
            # Вне диапазона (февраль)
            EventEntity(
                id="evt_002",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("500"), "RUB"),
                timestamp=datetime(2026, 2, 1),
            ),
            # В диапазоне
            EventEntity(
                id="evt_003",
                user_id=UserId("usr_1"),
                event_type=EventType.CLICK,
                money=None,
                timestamp=datetime(2026, 1, 20),
            ),
            # Вне диапазона (декабрь прошлого года)
            EventEntity(
                id="evt_004",
                user_id=UserId("usr_1"),
                event_type=EventType.VIEW,
                money=None,
                timestamp=datetime(2025, 12, 31),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 2  # Только evt_001 и evt_003
        assert stats.by_type == {EventType.PURCHASE: 1, EventType.CLICK: 1}
        assert stats.total_money == Money(Decimal("100"), "RUB")  # Только evt_001

    def test_aggregate_only_purchases_have_money(self, aggregator: EventAggregator):
        """Агрегация: money считается только для PURCHASE."""
        time_range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        events = [
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.CLICK,
                money=None,
                timestamp=datetime(2026, 1, 10),
            ),
            EventEntity(
                id="evt_002",
                user_id=UserId("usr_1"),
                event_type=EventType.VIEW,
                money=None,
                timestamp=datetime(2026, 1, 15),
            ),
            EventEntity(
                id="evt_003",
                user_id=UserId("usr_1"),
                event_type=EventType.REGISTRATION,
                money=None,
                timestamp=datetime(2026, 1, 20),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 3
        assert stats.by_type == {
            EventType.CLICK: 1,
            EventType.VIEW: 1,
            EventType.REGISTRATION: 1,
        }
        assert stats.total_money is None  # Нет PURCHASE

    def test_aggregate_boundary_time_range_start(
        self, aggregator: EventAggregator
    ):
        """Агрегация: событие на границе time_range (start)."""
        time_range = TimeRange(datetime(2026, 1, 1, 0, 0, 0), datetime(2026, 1, 31, 23, 59, 59))
        events = [
            # Ровно на start (включительно)
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 1, 0, 0, 0),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 1
        assert stats.by_type == {EventType.PURCHASE: 1}
        assert stats.total_money == Money(Decimal("100"), "RUB")

    def test_aggregate_boundary_time_range_end(self, aggregator: EventAggregator):
        """Агрегация: событие на границе time_range (end)."""
        time_range = TimeRange(datetime(2026, 1, 1, 0, 0, 0), datetime(2026, 1, 31, 23, 59, 59))
        events = [
            # Ровно на end (включительно)
            EventEntity(
                id="evt_001",
                user_id=UserId("usr_1"),
                event_type=EventType.PURCHASE,
                money=Money(Decimal("100"), "RUB"),
                timestamp=datetime(2026, 1, 31, 23, 59, 59),
            ),
        ]

        stats = aggregator.aggregate(events, time_range)

        assert stats.total_events == 1
        assert stats.by_type == {EventType.PURCHASE: 1}
        assert stats.total_money == Money(Decimal("100"), "RUB")
