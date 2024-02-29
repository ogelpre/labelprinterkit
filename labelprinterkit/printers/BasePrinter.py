from abc import ABC, abstractmethod
from typing import TypeVar

from ..backends import BaseBackend

BackendType = TypeVar('BackendType', bound=BaseBackend)


class BasePrinter(ABC):
    """Base class for printers. All printers define this API.  Any other
    methods are prefixed with a _ to indicate they are not part of the
    printer API"""

    def __init__(self, backend: BackendType):
        self._backend = backend

    @abstractmethod
    def print(self, job: 'Job'):
        ...


from ..job import Job
