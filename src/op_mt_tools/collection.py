from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from openpecha.core import ids as op_ids
from openpecha.utils import dump_yaml, load_yaml

LANG_CODE = str  # "bo" or "en"
PECHA_ID = str  # openpecha pecha id


class Metadata:
    def __init__(
        self,
        title: str,
        id: str = op_ids.get_collection_id(),
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
        items: List[Dict[LANG_CODE, PECHA_ID]] = [],
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
        path (Path): Path to the collection.
        metadata (Metadata): Metadata of the collection. If not provided, it will be
    """

    def __init__(
        self, path: Optional[Path] = None, metadata: Optional[Metadata] = None
    ):
        if not path and not metadata:
            raise ValueError("Either path or metadata must be provided.")

        self._path = path
        self._metadata = metadata
        self._base_path: Path = Path.home() / ".openpecha" / "collection"

    @property
    def path(self) -> Path:
        if not self._path:
            self._path = self._base_path / self.metadata.id
        return self._path

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

    def add_text_pair(
        self, text_pair: Dict[LANG_CODE, PECHA_ID]
    ) -> Dict[LANG_CODE, PECHA_ID]:
        self.metadata.items.append(text_pair)
        return text_pair

    def get_text_pairs(self) -> List[Dict[LANG_CODE, PECHA_ID]]:
        return self.metadata.items

    def save(self, output_path: Optional[Path] = None) -> Path:
        """Save the collection.

        Args:
            output_path (Path): Path to save the collection. If not provided, it will be
                saved to the default path (~/.openpecha/collections).

        Returns:
            Path: Path to the collection.
        """
        if output_path:
            self._base_path = output_path
        dump_yaml(self.metadata.to_dict(), self.meta_fn)
        return self.path
