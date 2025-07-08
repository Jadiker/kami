from enum import Enum
from typing import Any

class InfiniteColor(Enum):
    ORANGE = 0
    DARK_BLUE = 1
    CREAM = 2
    TURQUOISE = 3
    RED = 4

    @classmethod
    def _missing_(cls, value: Any) -> "InfiniteColor":
        if isinstance(value, int):
            name = f"Color_{value}"
            if name in cls.__members__:
                return cls.__members__[name]
            member = object.__new__(cls)
            member._name_ = name
            member._value_ = value
            cls._value2member_map_[value] = member
            cls._member_map_[name] = member
            return member
        raise ValueError(f"{value!r} is not a valid {cls.__name__}")

if __name__ == "__main__":
    new_color = InfiniteColor(10)
    print(new_color)
    print(type(new_color))
    print(new_color.name)
    print(new_color.value)
