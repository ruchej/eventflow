from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeRange:
    """Временной диапазон для запроса статистики.
    
    Value Object для представления периода "с ... по ...".
    Гарантирует, что начало периода раньше конца.
    
    Attributes:
        from_: Начало периода (включительно)
        to: Конец периода (включительно)
    
    Example:
        >>> from datetime import datetime
        >>> range = TimeRange(datetime(2026, 1, 1), datetime(2026, 1, 31))
        
        >>> TimeRange(datetime(2026, 1, 31), datetime(2026, 1, 1))  # ValueError
    """
    from_: datetime
    to: datetime

    def __post_init__(self) -> None:
        if self.to <= self.from_:
            raise ValueError("Значение периода to должно быть больше from_")

    def __contains__(self, dt: datetime) -> bool:
        """Поддержка оператора in."""
        return self.from_ <= dt <= self.to
