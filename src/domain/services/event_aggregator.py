from collections import defaultdict

from src.domain.entities import EventEntity, EventStatsEntity
from src.domain.value_objects import Money, TimeRange


class EventAggregator:
    """Аггрегатор состояний."""

    def aggregate(self, events: list[EventEntity], time_range: TimeRange) -> EventStatsEntity:
        """Сбор статистики событий.
        
        Args:
            events: Список событий для агрегации
            time_range: Временной диапазон для фильтрации
        
        Returns:
            EventStatsEntity: Агрегированная статистика
        """

        relevant_events = filter(lambda x: x.timestamp in time_range, events)
        total = 0
        by_type = defaultdict(int)
        total_money: Money | None = None

        for event in relevant_events:
            total += 1
            by_type[event.event_type] += 1
            if event.money:
                if total_money is None:
                    total_money = event.money
                else:
                    total_money += event.money

        return EventStatsEntity(
            time_range=time_range,
            total_events=total,
            by_type=by_type,
            total_money=total_money,
        )
