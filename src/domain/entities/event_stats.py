from dataclasses import dataclass

from src.domain.value_objects import EventType, Money, TimeRange


@dataclass(frozen=True, slots=True)
class EventStatsEntity:
    """Сущность статистики событий.

    Entity для определения статиситики событий.

    Attributes:
        time_range: Value Object TimeRange
        total_events: int
        by_type: dict[Value Object EventType, int]
        total_money: Value Object Money | None = None
    """
    time_range: TimeRange
    total_events: int
    by_type: dict[EventType, int]
    total_money: Money | None = None

    def __post_init__(self) -> None:
        if self.total_events < 0:
            raise ValueError("Значение total_events не должно быть меньше нуля")
        negative_by_type = next((key for key, value in self.by_type.items() if value < 0), None)
        if negative_by_type:
            raise ValueError("Значение количества событий по типам не должно быть отрицательным")
        if self.total_money and self.total_money.amount <= 0:
            raise ValueError("Значение суммы денег должно быть больше нуля")
