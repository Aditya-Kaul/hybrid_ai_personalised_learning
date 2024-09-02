import os
from typing import Any, Optional, Dict
from typing_extensions import override
from google.cloud import storage
from chromadb.config import System
from chromadb.api.types import Document
from chromadb.segment import SegmentImplementation, SegmentManager
from chromadb.api.models.Collection import Collection
from typing import Optional, List

class GCSStorage(SegmentImplementation):
    def __init__(self, system: System, bucket_name: str, path: str):
        super().__init__(system)
        self._bucket_name = bucket_name
        self._path = path
        self._client = storage.Client()
        self._bucket = self._client.bucket(self._bucket_name)

    @override
    def save(self, collection: Collection, segment_id: str, data: Any) -> None:
        blob = self._bucket.blob(f"{self._path}/{collection.name}/{segment_id}")
        blob.upload_from_string(data)

    @override
    def load(self, collection: Collection, segment_id: str) -> Optional[Any]:
        blob = self._bucket.blob(f"{self._path}/{collection.name}/{segment_id}")
        if blob.exists():
            return blob.download_as_string()
        return None

    @override
    def delete(self, collection: Collection, segment_id: str) -> None:
        blob = self._bucket.blob(f"{self._path}/{collection.name}/{segment_id}")
        if blob.exists():
            blob.delete()

    @override
    def count(self, collection: Collection) -> int:
        # Count all blobs with the prefix of the collection
        blobs = self._bucket.list_blobs(prefix=f"{self._path}/{collection.name}/")
        return sum(1 for _ in blobs)

    @override
    def max_seqid(self, collection: Collection) -> int:
        # Find the maximum sequence id of all blobs with the prefix of the collection
        blobs = self._bucket.list_blobs(prefix=f"{self._path}/{collection.name}/")
        max_id = 0
        for blob in blobs:
            try:
                segment_id = int(blob.name.split('/')[-1])
                if segment_id > max_id:
                    max_id = segment_id
            except ValueError:
                continue
        return max_id


class GCSSegmentManager(SegmentManager):
    def __init__(self, system: System, bucket_name: str, path: str):
        super().__init__(system)
        self._storage = None
        self._bucket_name = bucket_name
        self._path = path

    def _initialize_storage(self) -> GCSStorage:
        if self._storage is None:
            self._storage = GCSStorage(self._system, segment, self._bucket_name, self._path)
        return self._storage

    @override
    def get_segment(self, collection: Collection, id: str) -> SegmentImplementation:
        segment = Segment(collection, id)  # Assuming Segment is defined
        return self._initialize_storage(segment)

    @override
    def create_segment(self, collection: Collection, segment_id: Optional[str] = None) -> SegmentImplementation:
        segment = Segment(collection, segment_id)  # Assuming Segment is defined
        return self._initialize_storage(segment)

    @override
    def delete_segment(self, collection: Collection, segment_id: str) -> None:
        segment = Segment(collection, segment_id)  # Assuming Segment is defined
        storage = self._initialize_storage(segment)
        storage.delete(collection, segment_id)

    @override
    def get_persistent_ids(self, collection: Collection) -> list[str]:
        storage = self._initialize_storage(Segment(collection, None))  # Assuming Segment is defined
        # List all blobs with the prefix of the collection
        blobs = storage._bucket.list_blobs(prefix=f"{storage._path}/{collection.name}/")
        return [blob.name.split('/')[-1] for blob in blobs]

    # Implement the missing abstract methods
    @override
    def create_segments(self, collections: list[Collection]) -> None:
        for collection in collections:
            self.create_segment(collection)

    @override
    def delete_segments(self, collections: list[Collection]) -> None:
        for collection in collections:
            segment_ids = self.get_persistent_ids(collection)
            for segment_id in segment_ids:
                self.delete_segment(collection, segment_id)

    @override
    def hint_use_collection(self, collection: Collection) -> None:
        # This method might be used to provide some hint or preparation for using the collection
        # For now, we'll leave it as a pass-through function
        pass

