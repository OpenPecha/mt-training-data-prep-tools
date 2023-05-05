from pathlib import Path
from typing import Dict

LANG_CODE = str  # "bo" or "en"
PECHA_ID = str  # openpecha pecha id
TEXT_ID = str  # e.g. "BO0001" EN0001
TEXT_ID_NO_PREFIX = str  # e.g. "BO0001" -> "0001"
TEXT_PAIR_ID = Dict[LANG_CODE, TEXT_ID]
TEXT_PAIR_PATH = Dict[LANG_CODE, Path]
TEXT_PAIR_VIEW_PATH = Dict[
    LANG_CODE, Path
]  # e.g. {"bo": "./C0001/C0001.opc/views/plaintext/P0002-bo.txt", "en": "./C0001/C0001.opc/views/plaintext/P0001-en.txt"} # noqa: E501
