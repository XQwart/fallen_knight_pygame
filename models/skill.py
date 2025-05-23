"""Система скиллов персонажа."""
from __future__ import annotations

import pygame as pg
from enum import Enum, auto
from typing import Dict, Optional, Tuple, List

class SkillType(Enum):
    """Типы скиллов."""
    ATTACK = auto()    # Атакующий скилл
    DEFENSE = auto()   # Защитный скилл
    UTILITY = auto()   # Утилитарный скилл
    SPECIAL = auto()   # Особый скилл

class Skill:
    """Класс скилла персонажа."""
    
    def __init__(
        self, 
        name: str, 
        icon_path: str, 
        cooldown: float, 
        mana_cost: int,
        skill_type: SkillType,
        key: int,
    ):
        self.name = name
        self.icon_path = icon_path
        self.cooldown = cooldown  # в секундах
        self.mana_cost = mana_cost
        self.skill_type = skill_type
        self.key = key  # клавиша активации
        
        # Загружаем иконку
        try:
            self.icon = pg.image.load(icon_path).convert_alpha()
        except (FileNotFoundError, pg.error):
            # Создаем заглушку, если файл не найден
            self.icon = self._create_placeholder_icon()
        
        # Состояние скилла
        self.remaining_cooldown = 0.0
        self.last_used_time = 0
        self.is_equipped = False
        
    def _create_placeholder_icon(self) -> pg.Surface:
        """Создает временное изображение для иконки скилла."""
        surface = pg.Surface((64, 64), pg.SRCALPHA)
        
        # Заполняем основу скилла цветом в зависимости от типа
        if self.skill_type == SkillType.ATTACK:
            color = (200, 50, 50)  # Красный для атакующих
        elif self.skill_type == SkillType.DEFENSE:
            color = (50, 100, 200)  # Синий для защитных
        elif self.skill_type == SkillType.UTILITY:
            color = (50, 180, 50)  # Зелёный для утилитарных
        else:
            color = (180, 50, 180)  # Фиолетовый для особых
            
        pg.draw.rect(surface, color, (0, 0, 64, 64), border_radius=10)
        
        # Добавляем первую букву имени скилла
        font = pg.font.Font(None, 40)
        text = font.render(self.name[0].upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(32, 32))
        surface.blit(text, text_rect)
        
        return surface
        
    def update(self, dt: float) -> None:
        """Обновляет состояние скилла."""
        if self.remaining_cooldown > 0:
            self.remaining_cooldown = max(0, self.remaining_cooldown - dt)
            
    def use(self, current_time: int, player) -> bool:
        """Использовать скилл, если возможно."""
        # Проверяем КД и ману
        if self.remaining_cooldown > 0:
            return False
            
        if player.mana < self.mana_cost:
            return False
            
        # Применяем эффект скилла
        self._apply_effect(player)
        
        # Запускаем КД и тратим ману
        self.remaining_cooldown = self.cooldown
        self.last_used_time = current_time
        player.use_mana(self.mana_cost)
        
        return True
        
    def _apply_effect(self, player) -> None:
        """Применяет эффект скилла. Переопределяется в наследниках."""
        pass
        
    @property
    def cooldown_percent(self) -> float:
        """Возвращает процент оставшегося КД (1.0 = полный КД, 0.0 = готов)."""
        if self.cooldown <= 0:
            return 0.0
        return self.remaining_cooldown / self.cooldown

class SkillManager:
    """Управляет всеми доступными скиллами персонажа."""
    
    def __init__(self):
        self.available_skills: Dict[str, Skill] = {}
        self.equipped_skills: List[Optional[Skill]] = [None, None, None, None]
        self.key_bindings = [pg.K_1, pg.K_2, pg.K_3, pg.K_4]
        
    def add_skill(self, skill: Skill) -> None:
        """Добавляет новый скилл в список доступных."""
        self.available_skills[skill.name] = skill
        
    def equip_skill(self, skill_name: str, slot: int) -> bool:
        """Устанавливает скилл в указанный слот (0-3)."""
        if slot < 0 or slot >= len(self.equipped_skills):
            return False
            
        if skill_name not in self.available_skills:
            return False
            
        skill = self.available_skills[skill_name]
        
        # Если скилл уже экипирован в другой слот, убираем его оттуда
        for i, equipped in enumerate(self.equipped_skills):
            if equipped and equipped.name == skill_name:
                self.equipped_skills[i] = None
                
        # Устанавливаем в выбранный слот
        self.equipped_skills[slot] = skill
        skill.key = self.key_bindings[slot]
        skill.is_equipped = True
        
        return True
        
    def unequip_skill(self, slot: int) -> None:
        """Удаляет скилл из указанного слота."""
        if 0 <= slot < len(self.equipped_skills) and self.equipped_skills[slot]:
            self.equipped_skills[slot].is_equipped = False
            self.equipped_skills[slot] = None
            
    def update(self, dt: float) -> None:
        """Обновляет состояние всех скиллов."""
        for skill in self.available_skills.values():
            skill.update(dt)
            
    def get_skill_by_key(self, key: int) -> Optional[Skill]:
        """Возвращает скилл по нажатой клавише."""
        for i, binding in enumerate(self.key_bindings):
            if binding == key and self.equipped_skills[i]:
                return self.equipped_skills[i]
        return None
            
    def use_skill_by_key(self, key: int, player) -> bool:
        """Использует скилл по нажатой клавише."""
        skill = self.get_skill_by_key(key)
        if skill:
            return skill.use(pg.time.get_ticks(), player)
        return False

# Пример конкретных скиллов
class FireballSkill(Skill):
    """Скилл 'Огненный шар'."""
    
    def __init__(self, key: int = pg.K_1):
        super().__init__(
            name="Fireball",
            icon_path="assets/images/hud/skill_fireball.png",
            cooldown=5.0,
            mana_cost=25,
            skill_type=SkillType.ATTACK,
            key=key,
        )
        
    def _apply_effect(self, player) -> None:
        # Здесь будет логика создания огненного шара
        print("Fireball cast!")

class ShieldSkill(Skill):
    """Скилл 'Щит'."""
    
    def __init__(self, key: int = pg.K_2):
        super().__init__(
            name="Shield",
            icon_path="assets/images/hud/skill_shield.png", 
            cooldown=10.0,
            mana_cost=30,
            skill_type=SkillType.DEFENSE,
            key=key,
        )
        
    def _apply_effect(self, player) -> None:
        # Здесь будет логика активации защитного щита
        print("Shield activated!")

class HealSkill(Skill):
    """Скилл 'Лечение'."""
    
    def __init__(self, key: int = pg.K_3):
        super().__init__(
            name="Heal",
            icon_path="assets/images/hud/skill_heal.png",
            cooldown=15.0, 
            mana_cost=40,
            skill_type=SkillType.UTILITY,
            key=key,
        )
        
    def _apply_effect(self, player) -> None:
        # Восстанавливаем здоровье игроку
        heal_amount = 20
        player.health = min(100, player.health + heal_amount)
        print(f"Healed for {heal_amount}!")

class BlinkSkill(Skill):
    """Скилл 'Телепорт'."""
    
    def __init__(self, key: int = pg.K_4):
        super().__init__(
            name="Blink",
            icon_path="assets/images/hud/skill_blink.png",
            cooldown=7.0,
            mana_cost=20, 
            skill_type=SkillType.SPECIAL,
            key=key,
        )
        
    def _apply_effect(self, player) -> None:
        # Здесь будет логика телепорта
        # player.rect.x += 200  # Телепорт вперед на 200 пикселей
        print("Blink teleport!") 