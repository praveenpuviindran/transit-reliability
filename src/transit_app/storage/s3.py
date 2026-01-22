from __future__ import annotations

from dataclasses import dataclass

import boto3

from transit_app.storage.base import BlobStorage


@dataclass(frozen=True)
class S3BlobStorage(BlobStorage):
    bucket: str
    prefix: str = ""

    def read_bytes(self, key: str) -> bytes:
        s3 = boto3.client("s3")

        # Build full object key safely
        obj_key = f"{self.prefix.strip('/')}/{key}".lstrip("/") if self.prefix else key

        resp = s3.get_object(Bucket=self.bucket, Key=obj_key)
        return resp["Body"].read()
