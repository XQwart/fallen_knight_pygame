"""View игровой сцены: камера + отрисовка."""
from __future__ import annotations

import pygame as pg

from models.constants import BG_COLOR
from views.camera import Camera
from views.hud import HUD
from models.level import Level


class GameView:
    """Отрисовывает мир через камеру."""

    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.camera = Camera(*screen.get_size())
        self.hud = HUD(screen)

    def update_screen(self, screen: pg.Surface):
        """Обновляет ссылку на экран и размеры камеры при изменении экрана."""
        if self.screen is not screen:
            self.screen = screen
            self.camera.update_screen_size(*screen.get_size())
            self.hud.update_screen(screen)

    def update(self, player: pg.sprite.Sprite) -> None:
        self.camera.update(player)

    def draw(self, player: pg.sprite.Sprite, sprites: pg.sprite.AbstractGroup, level: Level) -> None:
        # Очищаем экран
        self.screen.fill(BG_COLOR)
        
        # Отрисовываем уровень через камеру
        level.run(self.camera)
        
        # Отрисовываем игровые объекты через камеру
        for spr in sprites:
            self.screen.blit(spr.image, self.camera.apply(spr))
        
        # Отрисовываем HUD поверх всего
        self.hud.draw(player)
        
        # Обновляем экран
        pg.display.flip()
