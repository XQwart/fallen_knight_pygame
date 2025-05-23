"""Контроллер игровой сцены."""
from __future__ import annotations

import pygame as pg

from controllers.scene_base import Scene
from models.player import Player
from models.constants import WORLD_WIDTH_PX, WORLD_HEIGHT_PX
from views.game_view import GameView


class GameController(Scene):
    """Платформер-геймплей."""

    def __init__(self, config, saved=None):
        super().__init__(config)

        x, y, hp = (saved or (100, 0, 100))
        self.player = Player(x, y, hp)
        self.player.rect.bottom = WORLD_HEIGHT_PX
        self.player.on_ground = True

        self.sprites = pg.sprite.GroupSingle(self.player)
        self.view = GameView(self.config.screen)

        kb = self.config.key_bindings
        self._down = {
            kb["left"]:   lambda: self.player.set_move_left(True),
            kb["right"]:  lambda: self.player.set_move_right(True),
            kb["jump"]:   self.player.jump,
            kb["sprint"]: self.player.toggle_sprint,
            kb["block"]:  self.player.start_block,
            pg.K_1:       lambda: self.player.use_skill(pg.K_1),
            pg.K_2:       lambda: self.player.use_skill(pg.K_2),
            pg.K_3:       lambda: self.player.use_skill(pg.K_3),
            pg.K_4:       lambda: self.player.use_skill(pg.K_4),
        }
        self._up = {
            kb["left"]:  lambda: self.player.set_move_left(False),
            kb["right"]: lambda: self.player.set_move_right(False),
            kb["block"]: self.player.stop_block,
        }

    # ---------------------------------------------------------------- events
    def handle_events(self) -> str | None:
        # Обновляем ссылку на экран, если он изменился
        if self.view.screen is not self.config.screen:
            self.view.update_screen(self.config.screen)
            
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                return "exit"
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_ESCAPE:
                    return "back"
                self._down.get(ev.key, lambda: None)()
            if ev.type == pg.KEYUP:
                self._up.get(ev.key, lambda: None)()
            if ev.type == pg.MOUSEBUTTONDOWN:
                self.player.handle_mouse(ev.type)
        return None

    # ---------------------------------------------------------------- model / draw
    def update_model(self) -> None:
        self.sprites.update()

        # приземление
        if self.player.rect.bottom >= WORLD_HEIGHT_PX:
            self.player.rect.bottom = WORLD_HEIGHT_PX
            self.player.vel_y, self.player.on_ground = 0, True

        # world bounds
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        if self.player.rect.right > WORLD_WIDTH_PX:
            self.player.rect.right = WORLD_WIDTH_PX

    def draw(self) -> None:
        self.view.update(self.player)
        self.view.draw(self.sprites)
