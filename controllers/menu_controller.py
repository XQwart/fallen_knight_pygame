"""Контроллер главного меню."""
from __future__ import annotations

import os
import pygame as pg

from controllers.scene_base import Scene
from views.menu_view import MenuView, MUSIC_END_EVENT


class MenuController(Scene):
    """Логика главного меню."""

    def __init__(self, config):
        super().__init__(config)
        can_continue = os.path.exists("savegame.dat")
        self.items = [
            ("CONTINUE", "continue", can_continue),
            ("NEW GAME", "new_game", True),
            ("SETTINGS", "settings", True),
            ("EXIT", "exit", True),
        ]
        view_data = [(txt, enabled) for txt, _, enabled in self.items]
        self.view = MenuView(self.config.screen, self.config, view_data)

    # Добавляем метод для обновления экрана
    def update_screen(self):
        """Обновляет ссылку на экран в представлении, если экран был пересоздан."""
        if self.view.screen is not self.config.screen:
            self.view.update_screen(self.config.screen)

    # ---------------------------------------------------------------- events
    def handle_events(self) -> str | None:
        # Обновляем ссылку на экран перед обработкой событий
        self.update_screen()
        
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                return "exit"
            if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
                return "exit"
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                for (txt, ident, ena), rect in zip(self.items, self.view.item_rects):
                    if ena and rect.collidepoint(ev.pos):
                        return ident
            if ev.type == MUSIC_END_EVENT:
                self.view.start_fade()
        return None

    # модель меню не изменяется
    def update_model(self) -> None: ...
    def draw(self) -> None:        self.view.draw()
