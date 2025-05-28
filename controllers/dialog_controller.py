"""Контроллер диалоговой сцены."""

from __future__ import annotations

import pygame as pg

from models.dialog import DialogModel
from views.dialog_view import DialogView


class DialogController:
    """Воспроизводит сюжетные реплики.

    Возвращает 'game' по завершении диалога,
    'exit' — если игрок закрыл окно.
    """

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.model: DialogModel | None = None
        self.screen = cfg.screen
        self.clock = pg.time.Clock()
        self.view = DialogView(None, self.screen, cfg)

        self.current = 0

    # ---------------------------------------------------------------- run
    def run(self) -> str | None:
        if not self.model:
            print("Ошибка: DialogModel не была установлена для DialogController.")
            return "menu"

        self.view.model = self.model
        self.current = 0
        pg.mixer.music.stop()
        self._play_sound_if_any()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "exit"
                if event.type == pg.KEYDOWN and event.key in (pg.K_SPACE, pg.K_RETURN):
                    if self.current < len(self.model) - 1:
                        self.current += 1
                        self._play_sound_if_any()
                    else:
                        pg.mixer.stop()
                        return "game"
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.current < len(self.model) - 1:
                        self.current += 1
                        self._play_sound_if_any()
                    else:
                        pg.mixer.stop()
                        return "game"

            self.screen.fill((0, 0, 0))
            self.view.draw(self.current)
            pg.display.flip()
            self.clock.tick(60)

    # ----------------------------------------------------------- helpers
    def _play_sound_if_any(self) -> None:
        pg.mixer.stop()
        
        entry = self.model.get(self.current)
        if entry.sound:
            pg.mixer.Sound(entry.sound).play()
