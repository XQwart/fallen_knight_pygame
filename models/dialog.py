"""Модель сюжетных диалогов.

Читает сценарий из ``assets/story.json`` (или ``assets/story.txt``) и
подготавливает список реплик.

Формат ``story.json``::

    [
      {
        "text": "В далёком королевстве люди жили в мире…",
        "image": "assets/story/world_map.png",
        "sound": "assets/sfx/intro.ogg",
        "speaker": "Рассказчик",
        "portrait": "assets/images/menu/storyteller.png"
      },
      …
    ]

Если файла *.json* нет, пробует ``story.txt`` — по строке на реплику
(формат: TEXT|image_path|sound_path).  Дополнительные поля можно опустить.

Модель не зависит от Pygame.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True, slots=True)
class DialogueEntry:
    text: str
    image: str | None = None
    sound: str | None = None
    speaker: str | None = None
    portrait: str | None = None


class DialogModel:
    """Загружает и предоставляет реплики по индексу."""

    def __init__(self, assets_dir: str = "assets/chapters/level_0/") -> None:
        self.entries: list[DialogueEntry] = self._load_script(Path(assets_dir))

    # ---------------------------------------------------------------- public
    def __len__(self) -> int:
        return len(self.entries)

    def get(self, index: int) -> DialogueEntry:
        return self.entries[index]

    # ---------------------------------------------------------------- intern
    @staticmethod
    def _load_script(root: Path) -> list[DialogueEntry]:
        story_json = root / "story.json"
        if story_json.exists():
            with story_json.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            for item in raw:
                if 'image' in item and item['image']:
                    # Пути в JSON уже должны быть относительно корня проекта, используем их напрямую
                    # item['image'] = str(Path(root.parent.parent) / item['image']).replace('\\\\', '/') # Старая некорректная строка
                    pass # Используем путь как есть
                if 'sound' in item and item['sound']:
                    # Пути в JSON уже должны быть относительно корня проекта, используем их напрямую
                    # item['sound'] = str(Path(root.parent.parent) / item['sound']).replace('\\\\', '/') # Старая некорректная строка
                    pass # Используем путь как есть
                if 'portrait' in item and item['portrait']:
                    # Пути в JSON уже должны быть относительно корня проекта, используем их напрямую
                    # item['portrait'] = str(Path(root.parent.parent) / item['portrait']).replace('\\\\', '/') # Старая некорректная строка
                    pass # Используем путь как есть
            return [DialogueEntry(**item) for item in raw]

        # ----- fallback: story.txt (|‑разделители) -------------------------
        story_txt = root / "story.txt"
        if story_txt.exists():
            result: list[DialogueEntry] = []
            with story_txt.open("r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    entry_data = {"text": parts[0]}
                    
                    # Добавляем остальные поля, если они есть
                    if len(parts) > 1 and parts[1]:
                        entry_data["image"] = parts[1]
                    if len(parts) > 2 and parts[2]:
                        entry_data["sound"] = parts[2]
                    if len(parts) > 3 and parts[3]:
                        entry_data["speaker"] = parts[3]
                    if len(parts) > 4 and parts[4]:
                        entry_data["portrait"] = parts[4]
                    
                    result.append(DialogueEntry(**entry_data))
            return result

        raise FileNotFoundError(
            f"Не найден сценарий '{story_json}' или 'assets/story.txt'"
        )
