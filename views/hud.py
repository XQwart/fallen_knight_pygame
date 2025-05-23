"""Отображение интерфейса игрока (HUD)."""
from __future__ import annotations

import pygame as pg
from models.player import Player


class HUD:
    """Отображает интерфейс игрока: здоровье, ману и монеты."""

    def __init__(self, screen: pg.Surface):
        self.screen = screen
        
        # Загружаем изображения для HUD
        try:
            self.portrait = pg.image.load("assets/images/hud/portrait.png").convert_alpha()
            self.heart_full = pg.image.load("assets/images/hud/heart_full.png").convert_alpha()
            self.heart_empty = pg.image.load("assets/images/hud/heart_empty.png").convert_alpha()
            self.coin_img = pg.image.load("assets/images/hud/coin.png").convert_alpha()
            self.mana_img = pg.image.load("assets/images/hud/mana.png").convert_alpha()
        except FileNotFoundError:
            # Создаем заглушки, если файлы не найдены
            self._create_placeholder_images()
        
        # Размеры элементов HUD
        self.portrait_size = (64, 64)
        self.heart_size = (24, 24)
        self.icon_size = (24, 24)
        
        # Масштабируем изображения
        self.portrait = pg.transform.scale(self.portrait, self.portrait_size)
        self.heart_full = pg.transform.scale(self.heart_full, self.heart_size)
        self.heart_empty = pg.transform.scale(self.heart_empty, self.heart_size)
        self.coin_img = pg.transform.scale(self.coin_img, self.icon_size)
        self.mana_img = pg.transform.scale(self.mana_img, self.icon_size)
        
        # Задаем шрифт для отображения текста
        self.font = pg.font.Font(None, 24)
        
        # Настройки отображения
        self.padding = 50  # Увеличенный отступ от края экрана
        self.heart_spacing = 2
        self.max_hearts = 10
        self.bar_height = 20
        self.element_margin = 10  # Отступ между элементами
        
        # Настройки для панели скиллов
        self.skill_slot_size = 64  # Размер слота скилла
        self.skill_slot_spacing = 10  # Расстояние между слотами
        self.skill_font = pg.font.Font(None, 20)  # Шрифт для отображения клавиш

    def update_screen(self, screen: pg.Surface):
        """Обновляет ссылку на экран."""
        self.screen = screen

    def draw(self, player: Player) -> None:
        """Отрисовывает интерфейс игрока."""
        # Основная позиция HUD в левом верхнем углу с отступом
        base_x, base_y = self.padding, self.padding
        
        # Фон для всего HUD (полупрозрачный)
        hud_width = 380  # Увеличенная ширина
        hud_height = 150  # Увеличенная высота
        hud_bg = pg.Surface((hud_width, hud_height), pg.SRCALPHA)
        pg.draw.rect(hud_bg, (0, 0, 0, 150), (0, 0, hud_width, hud_height), border_radius=10)
        self.screen.blit(hud_bg, (base_x, base_y))
        
        # Отрисовка портрета игрока (в левом верхнем углу HUD)
        portrait_x = base_x + 15
        portrait_y = base_y + 15
        portrait_border_rect = pg.Rect(portrait_x - 2, portrait_y - 2, 
                                  self.portrait_size[0] + 4, self.portrait_size[1] + 4)
        pg.draw.rect(self.screen, (139, 69, 19), portrait_border_rect, border_radius=4)
        self.screen.blit(self.portrait, (portrait_x, portrait_y))
        
        # Отрисовка сердечек (здоровье) в ряд справа от портрета, на уровне верхней части портрета
        health_percent = player.health / 100
        hearts_to_show = int(health_percent * self.max_hearts)
        
        hearts_start_x = portrait_x + self.portrait_size[0] + 20  # Увеличенный отступ
        hearts_start_y = portrait_y  # Теперь на одном уровне с верхней частью портрета
        
        # Полоска подложка под сердцами
        hearts_bg_width = (self.heart_size[0] + self.heart_spacing) * self.max_hearts + 20  # Увеличенная ширина фона
        hearts_bg_rect = pg.Rect(hearts_start_x - 10, hearts_start_y - 5, 
                             hearts_bg_width, self.heart_size[1] + 10)
        pg.draw.rect(self.screen, (80, 0, 0, 150), hearts_bg_rect, border_radius=4)
        
        for i in range(self.max_hearts):
            heart_x = hearts_start_x + i * (self.heart_size[0] + self.heart_spacing)
            heart_y = hearts_start_y
            
            if i < hearts_to_show:
                self.screen.blit(self.heart_full, (heart_x, heart_y))
            else:
                self.screen.blit(self.heart_empty, (heart_x, heart_y))
        
        # Отрисовка индикатора золота
        coin_bg_rect = pg.Rect(portrait_x, portrait_y + self.portrait_size[1] + 15, 100, 30)
        pg.draw.rect(self.screen, (139, 69, 19, 200), coin_bg_rect, border_radius=4)
        
        # Отрисовка монеты и текста (как было раньше)
        coin_x = portrait_x + 5
        coin_y = portrait_y + self.portrait_size[1] + 18
        self.screen.blit(self.coin_img, (coin_x, coin_y))
        
        coin_text = self.font.render(f"{getattr(player, 'coins', 0)}", True, (255, 215, 0))
        self.screen.blit(coin_text, (coin_x + self.icon_size[0] + 10, coin_y + 2))
        
        # Отрисовка полоски маны
        mana_bar_width = hearts_bg_width
        mana_bar_height = 20
        mana_bg_rect = pg.Rect(hearts_start_x - 10, hearts_start_y + self.heart_size[1] + 15, 
                           mana_bar_width, mana_bar_height)
        
        # Фон полоски (пустая)
        pg.draw.rect(self.screen, (30, 30, 80), mana_bg_rect, border_radius=4)
        
        # Заполненная часть полоски
        mana_percent = player.mana / player.max_mana
        mana_fill_width = int(mana_bar_width * mana_percent)
        mana_fill_rect = pg.Rect(hearts_start_x - 10, hearts_start_y + self.heart_size[1] + 15, 
                            mana_fill_width, mana_bar_height)
        pg.draw.rect(self.screen, (30, 30, 200), mana_fill_rect, border_radius=4)
        
        # Значение маны на самом баре
        mana_text = self.font.render(f"{player.mana}/{player.max_mana}", True, (200, 200, 255))
        
        # Центрируем текст маны по центру бара
        mana_text_x = hearts_start_x - 10 + (mana_bar_width - mana_text.get_width()) // 2
        mana_text_y = hearts_start_y + self.heart_size[1] + 15 + (mana_bar_height - mana_text.get_height()) // 2
        
        self.screen.blit(mana_text, (mana_text_x, mana_text_y))
        
        # Отрисовка панели скиллов
        self._draw_skill_bar(player)

    def _draw_skill_bar(self, player: Player) -> None:
        """Отрисовывает панель скиллов игрока."""
        # Вычисляем размеры панели скиллов
        num_skills = 4
        total_width = num_skills * self.skill_slot_size + (num_skills - 1) * self.skill_slot_spacing
        total_height = self.skill_slot_size + 30  # Дополнительное место для клавиш
        
        # Позиционируем панель снизу по центру
        skill_bar_x = (self.screen.get_width() - total_width) // 2
        skill_bar_y = self.screen.get_height() - total_height - 20  # Отступ от низа экрана
        
        # Создаем фоновую поверхность для панели скиллов
        skill_bg = pg.Surface((total_width + 20, total_height + 10), pg.SRCALPHA)
        pg.draw.rect(skill_bg, (0, 0, 0, 150), (0, 0, total_width + 20, total_height + 10), border_radius=8)
        self.screen.blit(skill_bg, (skill_bar_x - 10, skill_bar_y - 5))
        
        # Отрисовка каждого слота скилла
        for i in range(num_skills):
            slot_x = skill_bar_x + i * (self.skill_slot_size + self.skill_slot_spacing)
            slot_y = skill_bar_y
            
            # Фон слота (темный)
            slot_bg_rect = pg.Rect(slot_x, slot_y, self.skill_slot_size, self.skill_slot_size)
            pg.draw.rect(self.screen, (40, 40, 40), slot_bg_rect, border_radius=4)
            pg.draw.rect(self.screen, (100, 100, 100), slot_bg_rect, 2, border_radius=4)
            
            # Получаем скилл из менеджера скиллов
            skill = player.skill_manager.equipped_skills[i]
            
            if skill:
                # Отрисовка иконки скилла
                skill_icon = pg.transform.scale(skill.icon, (self.skill_slot_size - 4, self.skill_slot_size - 4))
                self.screen.blit(skill_icon, (slot_x + 2, slot_y + 2))
                
                # Отрисовка текста с клавишей активации
                key_text = self.skill_font.render(f"{i+1}", True, (255, 255, 255))
                key_rect = key_text.get_rect(center=(slot_x + self.skill_slot_size // 2, 
                                                 slot_y + self.skill_slot_size + 15))
                self.screen.blit(key_text, key_rect)
                
                # Отрисовка кулдауна (затемнение)
                if skill.remaining_cooldown > 0:
                    cooldown_overlay = pg.Surface((self.skill_slot_size - 4, self.skill_slot_size - 4), pg.SRCALPHA)
                    cooldown_overlay.fill((0, 0, 0, 180))
                    self.screen.blit(cooldown_overlay, (slot_x + 2, slot_y + 2))
                    
                    # Текст с оставшимся временем кулдауна
                    if skill.remaining_cooldown >= 1:
                        cd_text = self.skill_font.render(f"{int(skill.remaining_cooldown)}s", True, (255, 255, 255))
                    else:
                        cd_text = self.skill_font.render(f"{skill.remaining_cooldown:.1f}s", True, (255, 255, 255))
                    
                    cd_rect = cd_text.get_rect(center=(slot_x + self.skill_slot_size // 2, 
                                                   slot_y + self.skill_slot_size // 2))
                    self.screen.blit(cd_text, cd_rect)
                
                # Отрисовка стоимости маны
                mana_text = self.skill_font.render(f"{skill.mana_cost}", True, (100, 100, 255))
                mana_rect = mana_text.get_rect(bottomright=(slot_x + self.skill_slot_size - 4, 
                                                      slot_y + self.skill_slot_size - 4))
                self.screen.blit(mana_text, mana_rect)
            else:
                # Отрисовка пустого слота
                empty_text = self.skill_font.render(f"{i+1}", True, (150, 150, 150))
                empty_rect = empty_text.get_rect(center=(slot_x + self.skill_slot_size // 2, 
                                                    slot_y + self.skill_slot_size + 15))
                self.screen.blit(empty_text, empty_rect)

    def _create_placeholder_images(self):
        """Создает временные заглушки для изображений HUD."""
        # Создаем портрет
        self.portrait = pg.Surface((64, 64), pg.SRCALPHA)
        pg.draw.rect(self.portrait, (100, 100, 150), (0, 0, 64, 64))
        pg.draw.circle(self.portrait, (200, 180, 150), (32, 25), 15)  # голова
        pg.draw.rect(self.portrait, (100, 100, 150), (20, 40, 24, 24))  # тело
        
        # Создаем сердце (полное)
        self.heart_full = pg.Surface((24, 24), pg.SRCALPHA)
        pg.draw.polygon(self.heart_full, (255, 0, 0), 
                    [(12, 6), (6, 0), (0, 6), (0, 12), (12, 24), (24, 12), (24, 6), (18, 0)])
        
        # Создаем сердце (пустое)
        self.heart_empty = pg.Surface((24, 24), pg.SRCALPHA)
        pg.draw.polygon(self.heart_empty, (80, 0, 0), 
                    [(12, 6), (6, 0), (0, 6), (0, 12), (12, 24), (24, 12), (24, 6), (18, 0)], 2)
        
        # Создаем монету
        self.coin_img = pg.Surface((24, 24), pg.SRCALPHA)
        pg.draw.circle(self.coin_img, (255, 215, 0), (12, 12), 10)
        pg.draw.circle(self.coin_img, (200, 150, 0), (12, 12), 10, 2)
        
        # Создаем иконку маны
        self.mana_img = pg.Surface((24, 24), pg.SRCALPHA)
        pg.draw.circle(self.mana_img, (0, 0, 255), (12, 12), 10)
        pg.draw.circle(self.mana_img, (100, 100, 255), (12, 12), 6) 