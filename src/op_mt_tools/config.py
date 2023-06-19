from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

DATA_PATH = Path.home() / ".monlamAI" / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)

TEXTS_PATH = DATA_PATH / "texts"
TEXTS_PATH.mkdir(parents=True, exist_ok=True)

CLEANDED_TEXT_PREFIX = "[CLEANED]"
