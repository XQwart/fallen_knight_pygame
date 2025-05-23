"""Анимация спрайта."""
from __future__ import annotations

import pygame as pg


class Animation:
    """Зацикленные/одноразовые последовательности кадров."""

    def __init__(self, frames: list[pg.Surface], fps: int, *, loop: bool = True):
        self.frames, self.fps, self.loop = frames, fps, loop
        self.idx, self.playing, self.last = 0, False, 0

    def start(self) -> None:
        self.idx, self.playing, self.last = 0, True, pg.time.get_ticks()

    def stop(self) -> None:
        self.playing = False

    def update(self, *, flip_x=False, flip_y=False) -> pg.Surface:
        self._advance()
        frame = self.frames[self.idx]
        return pg.transform.flip(frame, flip_x, flip_y) if (flip_x or flip_y) else frame

    # ---------------------------------------------------------------------
    def _advance(self) -> None:
        if not self.playing:
            return
        if pg.time.get_ticks() - self.last >= 1000 // self.fps:
            self.idx += 1
            if self.idx >= len(self.frames):
                self.idx = 0
                if not self.loop:
                    self.playing = False
            self.last = pg.time.get_ticks()

    # ---------------------------------------------------------------------
    @property
    def finished(self) -> bool:
        return not self.loop and (not self.playing)
