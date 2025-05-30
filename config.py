import dataclasses
from pathlib import Path

from static import KeywordList
import json


def kw_load() -> list[KeywordList]:
    try:
        file = Path(__file__).parent / "config.json"
        if not file.exists():
            raise FileNotFoundError(f"Config file not found: {file}")

        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            KeywordList(name, elements)
            for name, elements in data.items()
            if isinstance(elements, list)
        ]
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {file}: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load keyword lists: {e}")
