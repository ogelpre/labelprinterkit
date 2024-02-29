from abc import ABC, abstractmethod


class BaseCommand(ABC):
    def __mul__(self, other) -> bytes:
        if not isinstance(other, int):
            raise TypeError("Can only multiply by an int")
        return self.to_bytes() * other

    @abstractmethod
    def to_bytes(self) -> bytes:
        ...
