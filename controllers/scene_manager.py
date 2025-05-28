"""Менеджер сцен — меню → диалог → настройки → игра."""
from __future__ import annotations

import pygame as pg

from controllers.menu_controller import MenuController
from controllers.settings_controller import SettingsController
from controllers.game_controller import GameController
from controllers.dialog_controller import DialogController
from models.dialog import DialogModel


class SceneManager:
    """Централизует создание и смену сцен."""

    def __init__(self, config):
        self.cfg = config
        self._menu_cache: MenuController | None = None   # сохраняем фон/музыку
        self.current_level_id: str = "level_0" # <--- Храним ID текущего уровня

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
                # <--- Загружаем модель диалога для текущего уровня ---
                dialog_model = DialogModel(f"assets/chapters/{self.current_level_id}/")
                controller = DialogController(self.cfg)
                controller.model = dialog_model # <--- Передаем модель в контроллер
            elif current == "settings":
                controller = SettingsController(self.cfg)
            elif current == "game":
                pg.mixer.music.stop()
                # <--- Передаем current_level_id в GameController ---
                controller = GameController(self.cfg, saved=saved, level_id=self.current_level_id)
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
                self.current_level_id = "level_0" # <--- Начинаем с уровня 0
                current = "dialog";                continue
            if result == "continue":
                # TODO: Нужно сохранять и загружать level_id вместе с 'saved'
                saved = self._load_save()
                # self.current_level_id = loaded_level_id
                current = "game";                  continue
            if result == "game":
                # Если диалог завершился, переходим в игру
                current = "game";                  continue
            # --- Добавляем обработку, если нужно будет менять уровень ---
            # if result.startswith("load_level_"):
            #     self.current_level_id = result.split("_")[-1]
            #     current = "game"; continue

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _load_save() -> tuple[int, int, int] | None:
        try:
            with open("savegame.dat") as f:
                x, y, hp = map(int, f.read().split())
            return (x, y, hp)
        except FileNotFoundError:
            return None
