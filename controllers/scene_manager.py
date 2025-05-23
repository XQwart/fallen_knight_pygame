"""Менеджер сцен — меню → диалог → настройки → игра."""
from __future__ import annotations

import pygame as pg

from controllers.menu_controller import MenuController
from controllers.settings_controller import SettingsController
from controllers.game_controller import GameController
from controllers.dialog_controller import DialogController


class SceneManager:
    """Централизует создание и смену сцен."""

    def __init__(self, config):
        self.cfg = config
        self._menu_cache: MenuController | None = None   # сохраняем фон/музыку

    # ---------------------------------------------------------------- run
    def run(self) -> None:
        current = "menu"
        saved: tuple[int, int, int] | None = None

        while True:
            # -------- создаём/берём нужный контроллер --------------------
            if current == "menu":
                self._menu_cache = self._menu_cache or MenuController(self.cfg)
                controller = self._menu_cache
            elif current == "dialog":
                controller = DialogController(self.cfg)
            elif current == "settings":
                controller = SettingsController(self.cfg)
            elif current == "game":
                pg.mixer.music.stop()
                controller = GameController(self.cfg, saved=saved)
            else:
                break

            # ---------------- запускаем сцену ----------------------------
            result = controller.run()

            # ---------------- интерпретируем результат -------------------
            if result in (None, "exit"):
                break
            if result == "settings":
                current = "settings";              continue
            if result == "back":
                current = "menu";                  continue
            if result == "new_game":
                saved = None
                current = "dialog";                continue
            if result == "continue":
                saved = self._load_save()
                current = "game";                  continue
            if result == "game":
                current = "game";                  continue

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _load_save() -> tuple[int, int, int] | None:
        try:
            with open("savegame.dat") as f:
                x, y, hp = map(int, f.read().split())
            return (x, y, hp)
        except FileNotFoundError:
            return None
