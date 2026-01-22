from __future__ import annotations

from abc import ABC, abstractmethod


class BlobStorage(ABC):
    """Abstract interface for reading binary objects (files) from some storage backend."""

    @abstractmethod
    def read_bytes(self, key: str) -> bytes:
        """Read the object located at `key` and return its bytes."""
        raise NotImplementedError
