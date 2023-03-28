import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from openpecha.core import ids as op_ids
from openpecha.core.pecha import OpenPechaGitRepo
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


class ViewMetadata:
    """Metadata for a view."""

    def __init__(
        self,
        id: str,
        serializer: str,
        views_path: Path,
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
    ):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.serializer = serializer
        self.views_path = views_path

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "serializer": self.serializer,
            "views_path": str(self.views_path),
        }

    @classmethod
    def from_dict(cls, data) -> "ViewMetadata":
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            serializer=data["serializer"],
            views_path=Path(data["views_path"]),
        )


SERIALIZERS_REGISTRY = {}


def register_serializer(name):
    def wrapper(fn):
        SERIALIZERS_REGISTRY[name] = fn
        return fn

    return wrapper


class ViewsEnum:
    PLAINTEXT = "plaintext"


@register_serializer(ViewsEnum.PLAINTEXT)
def text_pair_plaintext_serializer(
    text_pair: Dict[LANG_CODE, PECHA_ID],
    output_path: Path,
) -> Path:
    for lang_code, pecha_id in text_pair.items():
        pecha = OpenPechaGitRepo(pecha_id)
        pecha._opf_path = pecha._opf_path / f"{pecha_id}.opf"  # TODO: remove this hack
        pecha_view_path = output_path / pecha_id
        pecha_view_path.mkdir(parents=True, exist_ok=True)
        for base_name in pecha.components:
            source_path = pecha.base_path / f"{base_name}.txt"
            target_path = pecha_view_path / f"{base_name}-{lang_code}.txt"
            shutil.copy(source_path, target_path)
    return output_path


class View:
    """Class to represent a view of a collection.

    Args:
        base_path (Path): Path to the collection's views.
        id (str): Id of the view. If not provided, it will be generated.
        metadata (ViewMetadata): Metadata of the view. If not provided, it will be generated.
    """

    def __init__(
        self,
        base_path: Path,
        id: Optional[str] = None,
        metadata: Optional[ViewMetadata] = None,
    ):
        if not id and not metadata:
            raise ValueError("Either id or metadata must be provided.")

        self._id = id
        self._metadata = metadata
        self.base_path = base_path

    @property
    def path(self) -> Path:
        path = self.base_path / self.id_
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def meta_fn(self) -> Path:
        return self.path / "meta.yml"

    @property
    def id_(self) -> str:
        if self._id:
            return self._id
        self._id = self.metadata.id
        return self._id

    @property
    def metadata(self) -> ViewMetadata:
        if self._metadata:
            return self._metadata
        self._metadata = ViewMetadata.from_dict(load_yaml(self.meta_fn))
        return self._metadata

    def save_metadata(self):
        self.metadata.updated_at = datetime.now()
        dump_yaml(self.metadata.to_dict(), self.meta_fn)

    def generate(self, text_pair: Dict[LANG_CODE, PECHA_ID]) -> Path:
        self.save_metadata()
        serializer = SERIALIZERS_REGISTRY.get(self.id_)
        if serializer is None:
            raise ValueError(f"Serializer for {self.id_} not found.")
        output_path = serializer(text_pair, self.path)
        return output_path


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
    def views_path(self) -> Path:
        path = self.opa_path / "views"
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

    def create_view(self, view_id: str, text_pair: Dict[LANG_CODE, PECHA_ID]) -> Path:
        view = View(base_path=self.views_path, id=view_id)
        view_path = view.generate(text_pair)
        return view_path
