from datetime import datetime
from pathlib import Path
from typing import List, Optional

from openpecha.utils import dump_yaml, load_yaml


class Metadata:
    def __init__(
        self,
        id: str,
        title: str,
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
        items: List[str] = [],
    ):
        self.id = id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.items = items

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": self.items,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Metadata":
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            items=data["items"],
        )


class Collection:
    """A collection of pechas.

    Args:
        path: Path to the collection.
    """

    def __init__(self, path: Path, metadata: Optional[Metadata] = None):
        self.path = Path(path)
        self._metadata = metadata

    @property
    def opa_path(self) -> Path:
        path = self.path / f"{self.path.name}.opc"
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def meta_fn(self) -> Path:
        return self.opa_path / "meta.yml"

    @property
    def metadata(self) -> Metadata:
        if self._metadata:
            return self._metadata
        self._metadata = Metadata.from_dict(load_yaml(self.meta_fn))
        return self._metadata

    def set_pecha(self, pecha_id: str) -> str:
        self.metadata.items.append(pecha_id)
        return pecha_id

    def get_pechas(self) -> List[str]:
        return self.metadata.items

    def save(self) -> None:
        dump_yaml(self.metadata.to_dict(), self.meta_fn)
