from pathlib import Path

DATA_PATH = Path.home() / ".monlamAI" / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)
