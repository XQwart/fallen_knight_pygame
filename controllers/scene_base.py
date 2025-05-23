"""Абстрактный базовый класс любой сцены."""
from __future__ import annotations

from abc import ABC, abstractmethod
import pygame as pg


class Scene(ABC):
    """Общий цикл `run` и минимальный контракт для потомков-контроллеров."""

    def __init__(self, config):
        self.config = config
        self.clock = pg.time.Clock()

    # --------- обязательные методы-интерфейсы для наследников -------------
    @abstractmethod
    def handle_events(self) -> str | None: ...
    @abstractmethod
    def update_model(self) -> None: ...
    @abstractmethod
    def draw(self) -> None: ...

    # ----------------------------- цикл сцены -----------------------------
    def run(self) -> str | None:
        """
        Запускает цикл обработки событий/логики/рендера.

        Возвращает:
            идентификатор действия, по которому SceneManager
            решит, какую сцену запускать дальше.
        """
        next_action: str | None = None
        while next_action is None:
            next_action = self.handle_events()
            self.update_model()
            self.draw()
            self._tick()
        return next_action

    # ------------------------ ограничитель FPS ---------------------------
    def _tick(self) -> None:
        if self.config.vsync:
            self.clock.tick(0)
        else:
            self.clock.tick(self.config.fps_limit)
