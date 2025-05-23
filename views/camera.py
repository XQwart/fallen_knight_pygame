"""Камера удерживает персонажа в геометрическом центре окна."""
from __future__ import annotations

import pygame as pg

from models.constants import CAM_LERP


class Camera:
    """Плавный переход к желаемой позиции без ограничений по границам мира."""

    def __init__(self, w: int, h: int):
        self.scr_w, self.scr_h = w, h
        self.pos = pg.Vector2()

    def update_screen_size(self, w: int, h: int):
        """Обновить размеры экрана в камере."""
        self.scr_w, self.scr_h = w, h

    def update(self, target: pg.sprite.Sprite) -> None:
        """Перемещаем камеру так, чтобы цель была в центре."""
        desired = pg.Vector2(target.rect.center) - (self.scr_w / 2, self.scr_h / 2)
        self.pos += (desired - self.pos) * CAM_LERP

    def apply(self, spr: pg.sprite.Sprite) -> pg.Rect:
        return spr.rect.move(-self.pos.x, -self.pos.y)
