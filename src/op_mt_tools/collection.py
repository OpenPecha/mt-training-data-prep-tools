from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openpecha.core import ids as op_ids
from openpecha.core.pecha import OpenPechaGitRepo
from openpecha.utils import dump_yaml, load_yaml

from . import config
from . import types as t
from .tokenizers import sent_tokenize
from .utils import create_pecha, get_pkg_version


class Metadata:
    def __init__(
        self,
        title: str,
        id: str = op_ids.get_collection_id(),
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        items: List[Dict[t.LANG_CODE, t.PECHA_ID]] = [],
        imported_texts: List[Dict[t.TEXT_ID, t.PECHA_ID]] = [],
    ):
        self.id = id
        self.title = title
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
        self.items = items if items else []
        self.imported_texts = imported_texts if imported_texts else []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": self.items,
            "imported_texts": self.imported_texts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Metadata":
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            items=data["items"],
            imported_texts=data["imported_texts"],
        )


class ViewMetadata:
    """Metadata for a view."""

    def __init__(
        self,
        id: str,
        serializer: Optional[str] = None,
        views_path: Optional[Path] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
        self.serializer = serializer
        self.views_path = views_path if views_path else Path("views") / self.id

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
    text_pair: Dict[t.LANG_CODE, t.PECHA_ID],
    output_path: Path,
) -> Dict[t.LANG_CODE, Path]:
    """Serialize a text pair to plaintext."""

    text_pair_view_path = {}
    for lang_code, pecha_id in text_pair.items():
        pecha = OpenPechaGitRepo(pecha_id)
        pecha._opf_path = pecha._opf_path / f"{pecha_id}.opf"  # TODO: remove this hack
        pecha_view_fn = output_path / f"{pecha_id}-{lang_code}.txt"
        pecha_text = ""
        with pecha_view_fn.open("+a") as f:
            for base_name in pecha.base_names_list:
                pecha_text += pecha.get_base(base_name)
                sent_seg_text = sent_tokenize(text=pecha_text, lang=lang_code)
                f.write(sent_seg_text + "\n")
        text_pair_view_path[lang_code] = pecha_view_fn
    return text_pair_view_path


def get_serializer_path(serializer_name: str) -> str:
    serializer = SERIALIZERS_REGISTRY.get(serializer_name)
    if not serializer:
        raise ValueError(f"Serializer {serializer_name} not found.")
    pkg_name = Path(__file__).parent.name
    sub_pkg_name = Path(__file__).stem
    return f"{pkg_name}.{sub_pkg_name}.{serializer.__name__}@{get_pkg_version()}"


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
        if self.meta_fn.is_file():
            self._metadata = ViewMetadata.from_dict(load_yaml(self.meta_fn))
        else:
            if self._id:
                self._metadata = ViewMetadata(id=self._id)
            else:
                raise ValueError("Either id or metadata must be provided.")
        return self._metadata

    def save_metadata(self):
        self.metadata.updated_at = datetime.now()
        self.metadata.serializer = get_serializer_path(self.id_)
        dump_yaml(self.metadata.to_dict(), self.meta_fn)

    def generate(
        self, text_pair: Dict[t.LANG_CODE, t.PECHA_ID]
    ) -> Dict[t.LANG_CODE, Path]:
        self.save_metadata()
        serializer = SERIALIZERS_REGISTRY.get(self.id_)
        if serializer is None:
            raise ValueError(f"Serializer for {self.id_} not found.")
        text_pair_view_path = serializer(text_pair, self.path)
        return text_pair_view_path


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

    def is_text_added(self, text_id: t.TEXT_ID) -> bool:
        text_id = (
            text_id
            if text_id.startswith("BO") or text_id.startswith("EN")
            else f"BO{text_id}"
        )
        for imported_text in self.metadata.imported_texts:
            if text_id in imported_text:
                return True
        return False

    def add_text_pair(
        self, text_pair: Dict[t.LANG_CODE, t.PECHA_ID], text_id: t.TEXT_ID
    ) -> Dict[t.LANG_CODE, t.PECHA_ID]:
        self.metadata.items.append(text_pair)
        imported_text = {
            f"{lang.upper()}{text_id}": pecha_id for lang, pecha_id in text_pair.items()
        }
        self.metadata.imported_texts.append(imported_text)
        self.metadata.updated_at = datetime.now()
        return text_pair

    def get_text_pairs(self) -> List[Dict[t.LANG_CODE, t.PECHA_ID]]:
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

    def create_view(
        self, view_id: str, text_pair: Dict[t.LANG_CODE, t.PECHA_ID]
    ) -> Dict[t.LANG_CODE, Path]:
        view = View(base_path=self.views_path, id=view_id)
        text_pair_view_path = view.generate(text_pair)
        return text_pair_view_path


def add_text_pair_to_collection(
    text_pair_path: t.TEXT_PAIR_PATH, collection_path: Path
) -> Tuple[t.TEXT_ID_NO_PREFIX, t.TEXT_PAIR_VIEW_PATH]:
    """Add text pair to collection.

    Args:
        collection_path: Path to the collection.
        text_pair_path: Path to the text pair.
    """
    text_pair_ids = [fn.name for fn in text_pair_path.values()]
    collection = Collection(path=collection_path)
    text_id = text_pair_ids[0]
    if collection.is_text_added(text_id):
        print(f"[INFO] Text pair {text_pair_ids} is already to the collection...")
        return "", {}

    print(f"[INFO] Adding text pair {text_pair_ids} to the collection...")

    text_pair = {}
    output_path = config.DATA_PATH / "pechas"
    text_id_no_prefix = text_pair_ids[0][2:]
    for lang_code, path in text_pair_path.items():
        _, open_pecha_id = create_pecha(path, output_path=output_path)
        text_pair[lang_code] = open_pecha_id

    text_pair = collection.add_text_pair(text_pair, text_id_no_prefix)
    collection.save()
    text_pair_view_path = collection.create_view(
        view_id=ViewsEnum.PLAINTEXT, text_pair=text_pair
    )
    return text_id_no_prefix, text_pair_view_path


def skip_text(collection_path: Path, text_id: str) -> bool:
    """Check if text is already in the collection."""
    collection = Collection(path=collection_path)
    if collection.is_text_added(text_id):
        print(f"[INFO] Text pair {text_id} is already to the collection...")
        return True
    return False
