from __future__ import annotations

import pygame as pg
from models.config import Config
from controllers.scene_manager import SceneManager

if __name__ == "__main__":
    pg.init()
    pg.mixer.init()

    cfg = Config()
    cfg.create_display()

    SceneManager(cfg).run()

    cfg.save()
    pg.quit()
