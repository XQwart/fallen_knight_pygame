"""View‑часть диалоговой сцены."""

from __future__ import annotations

import pygame as pg
from models.dialog import DialogModel, DialogueEntry


class DialogView:
    """Отрисовывает текст, картинку и затемнение фона."""

    def __init__(self, model: DialogModel, screen: pg.Surface, cfg) -> None:
        self.model = model
        self.screen = screen
        self.cfg = cfg
        self.font = pg.font.Font(None, 32)
        self.name_font = pg.font.Font(None, 36)

        # Настраиваем диалоговое окно внизу экрана
        screen_height = screen.get_height()
        screen_width = screen.get_width()
        dialog_height = 160
        dialog_width = screen_width - 40
        
        self.text_box = pg.Rect(20, screen_height - dialog_height - 20,
                               dialog_width, dialog_height)
        
        # Настраиваем окно для имени говорящего
        self.name_box = pg.Rect(20, screen_height - dialog_height - 60,
                              200, 40)
        
        # Настраиваем область для портрета
        self.portrait_size = (120, 120)
        self.portrait_box = pg.Rect(30, screen_height - dialog_height - 10,
                                  self.portrait_size[0], self.portrait_size[1])
        
        # Создаём поверхности для фона диалоговых окон
        self._box_bg = pg.Surface(self.text_box.size, pg.SRCALPHA)
        self._box_bg.fill((0, 0, 0, 200))
        
        self._name_bg = pg.Surface(self.name_box.size, pg.SRCALPHA)
        self._name_bg.fill((50, 100, 50, 220))
        
        # Загружаем изображение рассказчика по умолчанию
        try:
            self.default_portrait = pg.image.load("assets/images/menu/storyteller.png").convert_alpha()
            self.default_portrait = pg.transform.scale(self.default_portrait, self.portrait_size)
        except FileNotFoundError:
            self.default_portrait = self._create_default_portrait()

    # ---------------------------------------------------------------- draw
    def draw(self, index: int) -> None:
        entry: DialogueEntry = self.model.get(index)

        # Рисуем фоновое изображение на весь экран (если есть)
        if entry.image:
            try:
                img = pg.image.load(entry.image).convert_alpha()
                img = pg.transform.scale(img, self.screen.get_size())
                self.screen.blit(img, (0, 0))
            except (pg.error, FileNotFoundError):
                # Если изображение не загрузилось, рисуем темный фон
                self.screen.fill((0, 0, 0))
        else:
            # Если изображения нет, просто рисуем темный фон
            self.screen.fill((0, 0, 0))

        # Легкое затемнение всего экрана для лучшей видимости текста
        dim = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        dim.fill((0, 0, 0, 100))
        self.screen.blit(dim, (0, 0))

        # Отрисовка имени говорящего
        self.screen.blit(self._name_bg, self.name_box.topleft)
        speaker_name = entry.speaker if hasattr(entry, 'speaker') and entry.speaker else "Рассказчик"
        name_text = self.name_font.render(speaker_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=self.name_box.center)
        self.screen.blit(name_text, name_rect)

        # Отрисовка текстового окна диалога
        self.screen.blit(self._box_bg, self.text_box.topleft)
        
        # Отрисовка портрета говорящего
        portrait = None
        if hasattr(entry, 'portrait') and entry.portrait:
            try:
                portrait = pg.image.load(entry.portrait).convert_alpha()
                portrait = pg.transform.scale(portrait, self.portrait_size)
            except (pg.error, FileNotFoundError):
                portrait = self.default_portrait
        else:
            portrait = self.default_portrait
            
        self.screen.blit(portrait, self.portrait_box.topleft)
        
        # Отрисовка текста диалога (с учетом отступа для портрета)
        text_area = pg.Rect(
            self.portrait_box.right + 20, 
            self.text_box.top + 20,
            self.text_box.width - self.portrait_size[0] - 40, 
            self.text_box.height - 40
        )
        self._render_text(entry.text, text_area)
        
        # Отрисовка индикатора прокрутки
        self._draw_scroll_indicator()

    # ----------------------------------------------------------- internals
    def _render_text(self, text: str, rect: pg.Rect) -> None:
        """Простейшая раскладка слов по строкам внутри прямоугольника."""
        words = text.split()
        space = self.font.size(" ")[0]
        x, y = rect.topleft
        max_w = rect.width
        for word in words:
            surf = self.font.render(word, True, (255, 255, 255))
            w, h = surf.get_size()
            if x + w >= rect.right:
                x = rect.left
                y += h
            self.screen.blit(surf, (x, y))
            x += w + space
            
    def _draw_scroll_indicator(self) -> None:
        """Рисует индикатор прокрутки (стрелка вниз) в нижней части диалогового окна."""
        # Рисуем треугольник как индикатор прокрутки
        triangle_center_x = self.text_box.centerx
        triangle_bottom_y = self.text_box.bottom - 15
        
        triangle_points = [
            (triangle_center_x - 10, triangle_bottom_y - 15),
            (triangle_center_x + 10, triangle_bottom_y - 15),
            (triangle_center_x, triangle_bottom_y)
        ]
        
        pg.draw.polygon(self.screen, (200, 200, 200), triangle_points)
            
    def _create_default_portrait(self) -> pg.Surface:
        """Создает заглушку для портрета говорящего."""
        portrait = pg.Surface(self.portrait_size, pg.SRCALPHA)
        
        # Фон
        pg.draw.rect(portrait, (50, 50, 80), (0, 0, *self.portrait_size), border_radius=10)
        
        # Силуэт головы
        head_center = (self.portrait_size[0] // 2, self.portrait_size[1] // 3)
        head_radius = min(self.portrait_size) // 4
        pg.draw.circle(portrait, (150, 150, 170), head_center, head_radius)
        
        # Силуэт тела
        body_rect = pg.Rect(
            self.portrait_size[0] // 4,
            self.portrait_size[1] // 2,
            self.portrait_size[0] // 2,
            self.portrait_size[1] // 3
        )
        pg.draw.rect(portrait, (120, 120, 140), body_rect, border_radius=5)
        
        return portrait
