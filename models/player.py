from __future__ import annotations
import random
from pathlib import Path
from enum import Enum, auto
import pygame as pg
from models.character import Character
from models.animation import Animation
from models.constants import BASE_SPEED, SPRINT_MULT, GRAVITY, JUMP_SPEED, MAX_FALL_SPEED, DOUBLE_CLICK_MS
from models.skill import SkillManager, FireballSkill, ShieldSkill, HealSkill, BlinkSkill

class PState(Enum):
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    ATTACK1 = auto()
    ATTACK2 = auto()
    HEAVY = auto()
    BLOCK = auto()
    HURT = auto()
    DEATH = auto()

# Словарь с информацией об анимациях: состояние -> (папка с кадрами, FPS, зациклена ли)
_ANIM_INFO = {
    PState.IDLE:    ("idle",        7,  True),
    PState.WALK:    ("walk",        8,  True),
    PState.RUN:     ("run",         8,  True),
    PState.ATTACK1: ("attack_1",    5,  False),
    PState.ATTACK2: ("attack_2",    5,  False),
    PState.HEAVY:   ("heavy_attack",6,  False),
    PState.BLOCK:   ("defend",      1,  True),
    PState.HURT:    ("hurt",        4,  False),
    PState.DEATH:   ("death",       12, False),
}

class Player(Character):
    """Класс игрока, включает движение, действия и анимационные состояния."""
    def __init__(self, x: int, y: int, health: int = 100) -> None:
        # Инициализируем персонажа с placeholder изображением (будет заменено анимацией)
        super().__init__("assets/images/hero_knight/placeholder.png", x, y, health=health)
        # Масштабируем спрайт-заглушку игрока до 128x128
        self.image = pg.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect(center=self.rect.center)
        self._state = PState.IDLE
        # Загружаем все анимации из папок ассетов
        self._animations = self._load_animations()
        self._animations[self._state].start()
        # Параметры движения и состояния
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self._sprint_on = False
        self._face_left = False
        self.left_down = False
        self.right_down = False
        self._last_rclick = 0
        
        # Параметры для HUD
        self.coins = 0
        self.mana = 100
        self.max_mana = 100
        
        # Инициализация системы скиллов
        self.skill_manager = SkillManager()
        self._init_default_skills()

    # ---------------- Управление вводом ----------------
    def set_move_left(self, down: bool) -> None:
        self.left_down = down
        self._recalc_vel_x()

    def set_move_right(self, down: bool) -> None:
        self.right_down = down
        self._recalc_vel_x()

    def jump(self) -> None:
        if self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

    def toggle_sprint(self) -> None:
        self._sprint_on = not self._sprint_on

    def start_block(self) -> None:
        self._enter_state(PState.BLOCK)

    def stop_block(self) -> None:
        if self._state == PState.BLOCK:
            self._enter_state(PState.IDLE)

    def handle_mouse(self, ev_type: int) -> None:
        if ev_type != pg.MOUSEBUTTONDOWN:
            return
        now = pg.time.get_ticks()
        lmb, _, rmb = pg.mouse.get_pressed(3)
        # Атаковать можно, только если игрок в состоянии Idle/Walk/Run (не занят другим)
        can_attack = self._state in {PState.IDLE, PState.WALK, PState.RUN}
        if lmb and can_attack:
            # Случайно выбираем одну из двух лёгких атак
            self._enter_state(random.choice([PState.ATTACK1, PState.ATTACK2]))
        elif rmb and can_attack:
            # Тяжёлая атака при двойном клике правой кнопкой
            if now - self._last_rclick <= DOUBLE_CLICK_MS:
                self._enter_state(PState.HEAVY)
                self._last_rclick = 0
            else:
                self._last_rclick = now
    
    def use_skill(self, key: int) -> bool:
        """Использует скилл по клавише."""
        # Скиллы можно использовать только если игрок не занят другим действием
        can_use_skill = self._state in {PState.IDLE, PState.WALK, PState.RUN}
        if can_use_skill:
            return self.skill_manager.use_skill_by_key(key, self)
        return False

    def get_speed(self) -> float:
        """Возвращает текущую скорость игрока."""
        return BASE_SPEED * (SPRINT_MULT if self._sprint_on else 1)

    def update(self) -> None:
        """Вызывается каждый кадр: обновляет FSM и анимацию."""
        self._update_state_machine()

        # Определяем направление взгляда по vel_x, если он не ноль
        if self.vel_x < 0:
            self._face_left = True
        elif self.vel_x > 0:
            self._face_left = False

        # Обновляем изображение
        self.image = self._animations[self._state].update(flip_x=self._face_left)

        # Обновляем скиллы
        dt = 1 / 60  # TODO: Использовать реальное время кадра
        self.skill_manager.update(dt)

    # ---------------- Методы управления ресурсами ----------------
    def add_coin(self, amount: int = 1) -> None:
        """Добавить монеты игроку."""
        self.coins += amount
    
    def spend_coins(self, amount: int) -> bool:
        """Потратить монеты, возвращает True если транзакция успешна."""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def add_mana(self, amount: int) -> None:
        """Добавить ману игроку."""
        self.mana = min(self.mana + amount, self.max_mana)
    
    def use_mana(self, amount: int) -> bool:
        """Использовать ману, возвращает True если достаточно маны."""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def take_damage(self, amount: int) -> None:
        """Получить урон. Обновлено для добавления анимации получения урона."""
        if self._state == PState.BLOCK:
            # Уменьшаем урон при блоке
            amount = max(1, amount // 2)
        
        super().take_damage(amount)
        
        if self.health <= 0:
            self._enter_state(PState.DEATH)
        else:
            self._enter_state(PState.HURT)
    
    def _init_default_skills(self) -> None:
        """Инициализация стандартного набора скиллов."""
        self.skill_manager.add_skill(FireballSkill(pg.K_1))
        self.skill_manager.add_skill(ShieldSkill(pg.K_2))
        self.skill_manager.add_skill(HealSkill(pg.K_3))
        self.skill_manager.add_skill(BlinkSkill(pg.K_4))
        
        # Экипируем скиллы по умолчанию
        self.skill_manager.equip_skill("Fireball", 0)
        self.skill_manager.equip_skill("Shield", 1)
        self.skill_manager.equip_skill("Heal", 2)
        self.skill_manager.equip_skill("Blink", 3)

    # ---------------- Внутренние методы состояния ----------------
    def _enter_state(self, new_state: PState) -> None:
        """Переключиться на новое состояние (анимацию)."""
        self._animations[self._state].stop()
        self._state = new_state
        self._animations[new_state].start()

    def _update_state_machine(self) -> None:
        """Логика переключения между анимационными состояниями."""
        if self._state in {PState.ATTACK1, PState.ATTACK2, PState.HEAVY, PState.HURT}:
            if self._animations[self._state].finished:
                self._enter_state(PState.IDLE)
            return
        if self._state == PState.DEATH:
            if self._animations[self._state].finished:
                self.kill() # Игрок умирает
            return
        if self._state == PState.BLOCK:
            return

        # --- Определяем состояние по vel_x ---
        moving = self.vel_x != 0 # Используем vel_x напрямую
        # --- Конец измененного кода ---

        desired_state = PState.RUN if self._sprint_on and moving else (PState.WALK if moving else PState.IDLE)
        if self._state != desired_state:
            self._enter_state(desired_state)

    def _recalc_vel_x(self) -> None:
        """Пересчитать горизонтальную скорость на основе флагов."""
        # Устанавливаем vel_x = 0, если обе или ни одна клавиша не нажата
        self.vel_x = 0
        if self.left_down and not self.right_down:
            self.vel_x = -1
        elif self.right_down and not self.left_down:
            self.vel_x = 1

    @staticmethod
    def _load_frames_from_folder(path: Path) -> list[pg.Surface]:
        """Загрузить и масштабировать все кадры анимации из указанной папки."""
        frames = []
        for img_path in sorted(path.glob("*.png")):
            frame = pg.image.load(img_path).convert_alpha()
            frame = pg.transform.scale(frame, (128, 128))
            frames.append(frame)
        return frames

    def _load_animations(self) -> dict[PState, Animation]:
        """Загрузить последовательности кадров для всех состояний игрока."""
        base_path = Path("assets/images/hero_knight")
        animations: dict[PState, Animation] = {}
        for state, (folder, fps, loop) in _ANIM_INFO.items():
            frames = self._load_frames_from_folder(base_path / folder)
            animations[state] = Animation(frames, fps, loop=loop)
        return animations
