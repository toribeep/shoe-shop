
from pathlib import Path
import sys


def resource_path(relative_path):
    """Возвращает путь к ресурсу внутри проекта или сборки PyInstaller."""
    if getattr(sys, "frozen", False):
        base_path = Path(__file__).resolve().parent
        internal_path = base_path / "_internal"

        if internal_path.exists():
            base_path = internal_path
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path
