from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

DATA_PATH = Path.home() / ".monlamAI" / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)

TEXTS_PATH = DATA_PATH / "texts"
TEXTS_PATH.mkdir(parents=True, exist_ok=True)

TMS_PATH = DATA_PATH / "tms"
TMS_PATH.mkdir(parents=True, exist_ok=True)

CLEANDED_TEXT_PREFIX = ""

LOGGING_PATH = DATA_PATH / "logs"
LOGGING_PATH.mkdir(parents=True, exist_ok=True)

QC_REVIEW_BRANCH_NAME = "qc-review"
