"""Настройки пользователя + управление отображением."""
from __future__ import annotations

import json
import os
from typing import Dict

import pygame as pg

_DEFAULT: Dict = {
    "key_bindings": {
        "left": pg.K_a,
        "right": pg.K_d,
        "jump": pg.K_SPACE,
        "sprint": pg.K_LCTRL,
        "block": pg.K_f,
    },
    "vsync": True,
    "fps_limit": 60,
    "fullscreen": True,
    "window_size": [1280, 720],
    "music_volume": 0.7,
}
_CFG = "config.json"


class Config:
    """Single Source of Truth для настроек."""

    def __init__(self) -> None:
        self.data = self._load()
        self.screen: pg.Surface | None = None

    # ----------------------------- props ----------------------------------
    key_bindings: Dict[str, int] = property(lambda self: self.data["key_bindings"])

    @property
    def vsync(self) -> bool:         return self.data["vsync"]
    @vsync.setter
    def vsync(self, v: bool):        self._set("vsync", bool(v))

    @property
    def fps_limit(self) -> int:      return self.data["fps_limit"]
    @fps_limit.setter
    def fps_limit(self, v: int):     self.data["fps_limit"] = int(v)

    @property
    def fullscreen(self) -> bool:    return self.data["fullscreen"]
    @fullscreen.setter
    def fullscreen(self, v: bool):   self._set("fullscreen", bool(v))

    window_size = property(lambda self: tuple(self.data["window_size"]))

    @property
    def music_volume(self) -> float: return self.data["music_volume"]
    @music_volume.setter
    def music_volume(self, v: float):
        self.data["music_volume"] = round(max(0.0, min(v, 1.0)), 1)
        pg.mixer.music.set_volume(self.data["music_volume"])

    # --------------------------- file ops ---------------------------------
    def _load(self) -> Dict:
        if os.path.exists(_CFG):
            try:
                with open(_CFG, encoding="utf8") as f:
                    return {**_DEFAULT, **json.load(f)}
            except Exception as ex:     # noqa: BLE001
                print("Config load error:", ex)
        return _DEFAULT.copy()

    def save(self) -> None:
        try:
            with open(_CFG, "w", encoding="utf8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as ex:        # noqa: BLE001
            print("Config save error:", ex)

    # ----------------------- display helpers ------------------------------
    def create_display(self) -> None:
        flags = pg.DOUBLEBUF | pg.RESIZABLE
        if self.fullscreen:
            flags |= pg.FULLSCREEN
            size = (0, 0)  # SDL выберет текущее разрешение
        else:
            size = self.window_size
            flags |= pg.SCALED  # Применяем SCALED только в оконном режиме
        vsync = 1 if self.vsync else 0
        
        # Не закрываем дисплей полностью, а только изменяем режим
        try:
            self.screen = pg.display.set_mode(size, flags, vsync=vsync)
            pg.display.set_caption("Fallen Knight")
        except pg.error as e:
            print(f"Ошибка при создании дисплея: {e}")
            # Попытка с минимальными параметрами
            flags = pg.RESIZABLE
            size = (960, 540)
            self.screen = pg.display.set_mode(size, flags)
            pg.display.set_caption("Fallen Knight")

    def _reset_display(self) -> None:
        """Пересоздаём окно.  Если RESIZABLE, при ошибке возвращаем safe-размер."""
        if not self.screen:
            return
        try:
            self.create_display()
        except pg.error as e:
            print(f"Ошибка при сбросе дисплея: {e}")
            # запасной вариант: маленькое окно, чтобы всегда влезало
            self.data["window_size"] = [960, 540]
            self.data["fullscreen"] = False  # Изменяем напрямую в data, чтобы избежать рекурсии
            
            # Не перезапускаем display модуль, а просто меняем режим
            try:
                self.screen = pg.display.set_mode((960, 540), pg.RESIZABLE)
                pg.display.set_caption("Fallen Knight")
            except pg.error as e2:
                print(f"Критическая ошибка дисплея: {e2}")

    # ---------------------------------------------------------------------
    def _set(self, key: str, value):   # общее изменение + пересоздание окна
        old_value = self.data.get(key)
        # Предотвращаем повторные вызовы при том же значении
        if old_value == value:
            return
        self.data[key] = value
        self._reset_display()
