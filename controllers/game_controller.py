# controllers/game_controller.py
import pygame as pg
from controllers.scene_base import Scene
from models.player import Player
# Убираем WORLD_WIDTH_PX, WORLD_HEIGHT_PX, так как размеры теперь зависят от уровня
from models.constants import GRAVITY, MAX_FALL_SPEED # Оставляем нужные константы
from views.game_view import GameView
from models.level import Level # <--- Импортируем Level

class GameController(Scene):
    """Платформер-геймплей."""

    def __init__(self, config, saved=None, level_id="level_0"): # <--- Добавляем level_id
        super().__init__(config)

        # Загружаем уровень <--- НОВОЕ
        self.level_id = level_id
        # Загружаем TMX файл уровня
        tmx_path = f"assets/chapters/{self.level_id}/tutorial.tmx"
        # Создаем объект уровня, передавая путь к TMX файлу
        self.level = Level(tmx_path)

        x, y, hp = (saved or (100, 100, 100)) # <--- Изменяем стартовую позицию
        self.player = Player(x, y, hp)
        # self.player.rect.bottom = WORLD_HEIGHT_PX # <--- Убираем привязку к низу мира
        # self.player.on_ground = True              # <--- Игрок начинает в воздухе

        self.sprites = pg.sprite.Group(self.player) # <--- Используем Group для всех спрайтов
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
        # Обновляем игрока (анимации, внутреннюю логику)
        self.sprites.update()

        # Применяем гравитацию <--- НОВОЕ
        self._apply_gravity()

        # Обрабатываем коллизии <--- НОВОЕ
        self._handle_collisions()

        # Проверяем границы мира (можно будет убрать или изменить на основе уровня)
        # if self.player.rect.left < 0:
        #     self.player.rect.left = 0
        # if self.player.rect.right > WORLD_WIDTH_PX:
        #     self.player.rect.right = WORLD_WIDTH_PX

    def _apply_gravity(self):
        """Применяет гравитацию к игроку."""
        self.player.vel_y = min(self.player.vel_y + GRAVITY, MAX_FALL_SPEED)
        # Мы не ставим on_ground здесь, это сделает обработчик коллизий

    def _handle_collisions(self):
        """Обрабатывает коллизии игрока с уровнем."""
        player = self.player
        collidable_tiles = self.level.collidable_tiles

        # Горизонтальное движение и коллизии
        player.rect.x += round(player.vel_x * player.get_speed())
        hit_list = pg.sprite.spritecollide(player, collidable_tiles, False)
        for tile in hit_list:
            if player.vel_x > 0: # Движение вправо
                player.rect.right = tile.rect.left
            elif player.vel_x < 0: # Движение влево
                player.rect.left = tile.rect.right
        player.vel_x = 0 # Сбрасываем vel_x после проверки, так как set_move_* его установит
        player._recalc_vel_x() # Пересчитываем на основе нажатых клавиш


        # Вертикальное движение и коллизии
        player.rect.y += round(player.vel_y)
        hit_list = pg.sprite.spritecollide(player, collidable_tiles, False)
        player.on_ground = False # Считаем, что игрок в воздухе, пока не найдем опору
        for tile in hit_list:
            if player.vel_y > 0: # Движение вниз
                player.rect.bottom = tile.rect.top
                player.vel_y = 0
                player.on_ground = True # Нашли опору
            elif player.vel_y < 0: # Движение вверх
                player.rect.top = tile.rect.bottom
                player.vel_y = 0

    def draw(self) -> None:
        self.view.update(self.player)
        # Передаем и спрайты, и уровень для отрисовки <--- ИЗМЕНЕНО
        self.view.draw(self.player, self.sprites, self.level) # Передаем спрайт игрока отдельно