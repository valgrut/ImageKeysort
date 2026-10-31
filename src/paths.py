import sys
from pathlib import Path


def asset_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset(*parts: str) -> Path:
    return asset_root().joinpath(*parts)
