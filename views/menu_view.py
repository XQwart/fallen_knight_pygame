"""View главного меню (фон + музыка)."""
from __future__ import annotations

import random
from typing import List, Tuple

import pygame as pg

BG_IMAGES = [
    "assets/images/menu/bg1.png",
    "assets/images/menu/bg2.png",
    "assets/images/menu/bg3.png",
]
BG_MUSIC = [
    "assets/sounds/menu1.ogg",
    "assets/sounds/menu2.ogg",
    "assets/sounds/menu3.ogg",
]
MUSIC_END_EVENT = pg.USEREVENT + 1


class MenuView:
    """Фон + музыка + рендер пунктов меню."""

    def __init__(self, screen: pg.Surface, cfg, items: List[Tuple[str, bool]]):
        self.screen, self.cfg = screen, cfg
        self.font = pg.font.SysFont(None, 60)
        self.original_images = [pg.image.load(p).convert() for p in BG_IMAGES]
        self.bgs = [pg.transform.scale(img, screen.get_size()) for img in self.original_images]
        self.idx = random.randrange(len(self.bgs))
        self.current_bg = self.bgs[self.idx]
        self._play_music(self.idx)

        self.fade, self.next_bg, self.next_idx = False, None, None
        self.fade_t0, self.fade_dur = 0, 1000

        self.items, self.item_rects = items, []
        self._layout_items()

    # ---------------------------------------------------------------- private
    def _layout_items(self) -> None:
        spacing, h = 20, self.font.get_height()
        total = len(self.items) * h + (len(self.items) - 1) * spacing
        y = (self.screen.get_height() - total) // 2
        cx = self.screen.get_width() // 2
        for txt, _ in self.items:
            w = self.font.size(txt)[0]
            rect = pg.Rect(0, 0, w, h)
            rect.midtop = (cx, y)
            self.item_rects.append(rect)
            y += h + spacing

    def _play_music(self, index: int) -> None:
        pg.mixer.music.load(BG_MUSIC[index])
        pg.mixer.music.set_volume(self.cfg.music_volume)
        pg.mixer.music.play()
        pg.mixer.music.set_endevent(MUSIC_END_EVENT)

    # ---------------------------------------------------------------- fade
    def start_fade(self) -> None:
        nxt = (self.idx + random.randint(1, len(self.bgs) - 1)) % len(self.bgs)
        self.next_idx, self.next_bg = nxt, self.bgs[nxt].copy()
        self.next_bg.set_alpha(0)
        self.fade, self.fade_t0 = True, pg.time.get_ticks()
        self._play_music(nxt)

    def _update_fade(self) -> None:
        alpha = min(255, int(255 * (pg.time.get_ticks() - self.fade_t0) / self.fade_dur))
        self.next_bg.set_alpha(alpha)
        if alpha >= 255:
            self.idx, self.current_bg = self.next_idx, self.bgs[self.next_idx]
            self.fade, self.next_bg = False, None

    # ---------------------------------------------------------------- draw
    def draw(self) -> None:
        if self.fade:
            self._update_fade()

        self.screen.blit(self.current_bg, (0, 0))
        if self.fade and self.next_bg:
            self.screen.blit(self.next_bg, (0, 0))

        mx, my = pg.mouse.get_pos()
        for (txt, ena), rect in zip(self.items, self.item_rects):
            color = (255, 255, 255) if (ena and rect.collidepoint((mx, my))) else (200, 200, 200 if ena else 120)
            self.screen.blit(self.font.render(txt, True, color), rect)
        pg.display.flip()

    def update_screen(self, screen: pg.Surface) -> None:
        """Обновляет ссылку на экран и пересчитывает размеры UI при изменении размера экрана."""
        if self.screen is screen:
            return
            
        self.screen = screen
        # Пересоздаем масштабированные фоны
        self.bgs = [pg.transform.scale(img, screen.get_size()) for img in self.original_images]
        self.current_bg = self.bgs[self.idx]
        
        # Если у нас активен переход, обновляем и его
        if self.fade and self.next_bg:
            self.next_bg = pg.transform.scale(self.original_images[self.next_idx], screen.get_size())
            self.next_bg.set_alpha(self.next_bg.get_alpha())
        
        # Перерасчитываем позиции пунктов меню
        self.item_rects = []
        self._layout_items()
