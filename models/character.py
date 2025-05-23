"""Базовый персонаж."""
from __future__ import annotations

import os
from pathlib import Path

import pygame as pg


class Character(pg.sprite.Sprite):
    """Общее для игрока и NPC."""

    def __init__(self, img_path: str | Path, x: int, y: int, *, health: int = 100):
        super().__init__()
        self.image = self._load(img_path)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health

    @staticmethod
    def _load(path: str | Path) -> pg.Surface:
        if not os.path.exists(path):
            s = pg.Surface((128, 128), pg.SRCALPHA)
            s.fill((255, 0, 255))
            return s
        return pg.transform.scale(pg.image.load(path).convert_alpha(), (128, 128))
