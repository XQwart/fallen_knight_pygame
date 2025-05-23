"""Отрисовка меню настроек."""
from __future__ import annotations

from typing import List, Tuple

import pygame as pg
from models.constants import BG_COLOR


class SettingsView:
    """Показывает все опции, подсвечивает, ждёт ввод клавиши."""

    def __init__(self, screen: pg.Surface, cfg, options: List[Tuple[str, str, str]]):
        self.screen, self.cfg, self.options = screen, cfg, options
        self.font, self.spacing = pg.font.SysFont(None, 48), 15
        self.waiting_for: str | None = None

    def update_screen(self, screen: pg.Surface) -> None:
        """Обновляет ссылку на экран при изменении размера экрана."""
        self.screen = screen
        # Не требуется перерасчета данных, так как все вычисляется динамически в draw

    # ---------------------------------------------------------------- utils
    def _fmt(self, text, ident, typ) -> str:
        if typ == "key":
            return f"{text}: {pg.key.name(self.cfg.key_bindings[ident]).upper()}"
        if ident == "vsync":
            return f"{text}: {'ON' if self.cfg.vsync else 'OFF'}"
        if ident == "fps":
            return f"{text}: {self.cfg.fps_limit}"
        if ident == "screen":
            mode = "FULL" if self.cfg.fullscreen else "WINDOW"
            return f"{text}: {mode}"
        if ident == "volume":
            return f"{text}: {int(self.cfg.music_volume * 100)}%"
        return text

    def _rect(self, y: int, txt: str) -> pg.Rect:
        w, h = self.font.size(txt)
        rect = pg.Rect(0, 0, w, h)
        rect.centerx, rect.top = self.screen.get_width() // 2, y
        return rect

    def ident_at(self, pos) -> tuple[str | None, str | None]:
        total = len(self.options) * self.font.get_height() + (len(self.options) - 1) * self.spacing
        y = (self.screen.get_height() - total) // 2
        for text, ident, typ in self.options:
            r = self._rect(y, self._fmt(text, ident, typ))
            if r.collidepoint(pos):
                return ident, typ
            y += self.font.get_height() + self.spacing
        return None, None

    # ---------------------------------------------------------------- draw
    def draw(self) -> None:
        self.screen.fill(BG_COLOR)
        total = len(self.options) * self.font.get_height() + (len(self.options) - 1) * self.spacing
        y = (self.screen.get_height() - total) // 2
        mx, my = pg.mouse.get_pos()

        for text, ident, typ in self.options:
            display = "Press new key..." if self.waiting_for == ident else self._fmt(text, ident, typ)
            rect = self._rect(y, display)
            hover = rect.collidepoint((mx, my))
            color = (180, 230, 255) if hover and typ != "action" else (255, 255, 255)
            self.screen.blit(self.font.render(display, True, color), rect)
            y += self.font.get_height() + self.spacing

        pg.display.flip()
