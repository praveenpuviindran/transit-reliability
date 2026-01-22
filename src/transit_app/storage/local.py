from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from transit_app.storage.base import BlobStorage


@dataclass(frozen=True)
class LocalBlobStorage(BlobStorage):
    base_dir: Path

    def read_bytes(self, key: str) -> bytes:
        path = self.base_dir / key
        return path.read_bytes()
