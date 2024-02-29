from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NewType, Type

from labelprinterkit.commands.BaseCommand import BaseCommand


class BaseBackend(ABC):
    ...


Command = NewType('Command', BaseCommand)


class UniDirectionalBackend(BaseBackend):
    @abstractmethod
    def write(self, data: bytes | Type[Command]):
        ...


class BiDirectionalBackend(UniDirectionalBackend):
    @abstractmethod
    def read(self, count: int) -> bytes:
        ...
