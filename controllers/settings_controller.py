"""Контроллер меню настроек."""
from __future__ import annotations

import pygame as pg

from controllers.scene_base import Scene
from views.settings_view import SettingsView

ALLOWED_FPS = [30, 60, 90, 120, 144, 165, 180, 200, 240]

OPTIONS = [
    ("Move Left",     "left",   "key"),
    ("Move Right",    "right",  "key"),
    ("Jump",          "jump",   "key"),
    ("Sprint",        "sprint", "key"),
    ("Block",         "block",  "key"),
    ("VSync",         "vsync",  "toggle"),
    ("FPS Limit",     "fps",    "slider"),
    ("Screen Mode",   "screen", "toggle"),
    ("Music Volume",  "volume", "slider"),
    ("Back",          "back",   "action"),
]


class SettingsController(Scene):
    """Настройки: клавиши, видео, громкость."""

    def __init__(self, config):
        super().__init__(config)
        self.wait_key: str | None = None
        self.view = SettingsView(self.config.screen, self.config, OPTIONS)

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

            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_ESCAPE and self.wait_key is None:
                    return "back"
                if self.wait_key:
                    self._apply_key(ev.key)

            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1 and self.wait_key is None:
                result = self._click(ev.pos)
                if result:
                    return result
        return None

    # ---------------------------------------------------------------- model/view
    def update_model(self) -> None: ...
    def draw(self) -> None:        self.view.draw()

    # ---------------------------------------------------------------- helpers
    def _click(self, pos) -> str | None:
        ident, typ = self.view.ident_at(pos)
        if ident is None:
            return None

        if typ == "key":
            self.wait_key, self.view.waiting_for = ident, ident
            return None

        if ident == "vsync":
            self.config.vsync = not self.config.vsync
        elif ident == "fps" and not self.config.vsync:
            idx = ALLOWED_FPS.index(self.config.fps_limit)
            self.config.fps_limit = ALLOWED_FPS[(idx + 1) % len(ALLOWED_FPS)]
        elif ident == "screen":
            new_mode = not self.config.fullscreen
            self.config.data["fullscreen"] = new_mode
            
            flags = pg.DOUBLEBUF | pg.RESIZABLE
            if new_mode:
                flags |= pg.FULLSCREEN
                size = (0, 0)
            else:
                size = self.config.window_size
                flags |= pg.SCALED
                
            try:
                vsync = 1 if self.config.vsync else 0
                self.config.screen = pg.display.set_mode(size, flags, vsync=vsync)
            except pg.error:
                self.config.data["window_size"] = [960, 540]
                self.config.data["fullscreen"] = False
                self.config.screen = pg.display.set_mode((960, 540), pg.RESIZABLE)
                
            pg.display.set_caption("Fallen Knight")
        elif ident == "volume":
            self.config.music_volume = 0.0 if self.config.music_volume >= 0.9 else round(self.config.music_volume + 0.1, 1)
        elif ident == "back":
            return "back"
        
        return None

    def _apply_key(self, keycode: int) -> None:
        # исключаем дубли
        for act, kc in self.config.key_bindings.items():
            if kc == keycode:
                self.config.key_bindings[act] = self.config.key_bindings[self.wait_key]
        self.config.key_bindings[self.wait_key] = keycode
        self.wait_key, self.view.waiting_for = None, None
