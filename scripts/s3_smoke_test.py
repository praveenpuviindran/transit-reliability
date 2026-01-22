from __future__ import annotations

from transit_app.storage.s3 import S3BlobStorage
from transit_app.repositories.reference import ReferenceRepository


def main() -> None:
    storage = S3BlobStorage(bucket="praveen-transit-reliability-ref-2026", prefix="reference")
    repo = ReferenceRepository(storage)

    stops = repo.list_stops()
    routes = repo.list_routes()

    print("stops:", len(stops))
    print("first stop:", stops[0])
    print("routes:", len(routes))
    print("first route:", routes[0])


if __name__ == "__main__":
    main()
