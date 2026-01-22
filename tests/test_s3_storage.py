from __future__ import annotations

from transit_app.storage.s3 import S3BlobStorage


class FakeBotoClient:
    def __init__(self, expected_bucket: str, expected_key: str, payload: bytes) -> None:
        self.expected_bucket = expected_bucket
        self.expected_key = expected_key
        self.payload = payload

    def get_object(self, Bucket: str, Key: str):
        assert Bucket == self.expected_bucket
        assert Key == self.expected_key

        class Body:
            def __init__(self, payload: bytes) -> None:
                self._payload = payload

            def read(self) -> bytes:
                return self._payload

        return {"Body": Body(self.payload)}


def test_s3_blob_storage_reads_bytes(monkeypatch):
    import transit_app.storage.s3 as s3mod

    fake = FakeBotoClient(expected_bucket="my-bucket", expected_key="ref/stops_min.json", payload=b"abc")

    def fake_client(service_name: str):
        assert service_name == "s3"
        return fake

    monkeypatch.setattr(s3mod.boto3, "client", fake_client)

    storage = S3BlobStorage(bucket="my-bucket", prefix="ref")
    data = storage.read_bytes("stops_min.json")
    assert data == b"abc"
