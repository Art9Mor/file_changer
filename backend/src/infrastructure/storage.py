from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BACKEND_ROOT / "storage" / "files"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def stored_file_path(stored_name: str) -> Path:
    """
    Абсолютный путь к объекту в хранилище.
    """

    return STORAGE_DIR / stored_name
