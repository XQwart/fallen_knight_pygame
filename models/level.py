import pygame as pg
import csv
from models.constants import TILE_SIZE
import os
import pytmx # Импортируем библиотеку для работы с TMX файлами

class Tile(pg.sprite.Sprite):
    """Представляет один тайл уровня."""
    def __init__(self, image: pg.Surface, x: int, y: int):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class Level:
    """Загружает и хранит данные уровня, создает тайлы."""

    def __init__(self, tmx_path: str, tile_assets_path: str = "assets/textures/map/"): # Меняем csv_path на tmx_path
        self.display_surface = pg.display.get_surface()
        self.tiles = pg.sprite.Group()  # Группа для всех тайлов (для отрисовки)
        self.collidable_tiles = pg.sprite.Group() # Группа для тайлов с коллизией
        self.tile_assets_path = tile_assets_path # Сохраняем путь к ассетам тайлов

        # Загрузка TMX карты
        self.tmx_data = self._load_tmx(tmx_path) # Новый метод загрузки TMX
        self.tile_size = self.tmx_data.tilewidth # Берем размер тайла из TMX данных

        # Создание уровня из TMX данных
        self._create_level() # Создаем спрайты на основе TMX

    def _load_tmx(self, path: str):
        """Загружает данные уровня из TMX файла."""
        try:
            # Передаем правильный путь к папке с ассетами тайлов
            tmx_data = pytmx.load_pygame(path, gidmap='base64', folder=self.tile_assets_path)
            return tmx_data
        except Exception as e:
            print(f"Ошибка загрузки TMX файла {path}: {e}")
            return None # Возвращаем None в случае ошибки загрузки

    def _create_level(self) -> None:
        """Создает спрайты тайлов на основе загруженных TMX данных."""
        if not self.tmx_data:
            return # Ничего не создаем, если TMX данные не загружены

        # Итерируем по всем видимым слоям TMX карты
        for layer in self.tmx_data.visible_layers:
            # Проверяем, является ли слой слоем с тайлами
            if isinstance(layer, pytmx.TiledTileLayer):
                # Итерируем по всем тайлам в слое
                for x, y, gid, in layer:
                    # Проверяем, не является ли тайл пустым (GID 0)
                    if gid != 0:
                        # Получаем изображение тайла по его GID
                        tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile_image:
                            # Получаем свойства тайла из TMX данных
                            props = self.tmx_data.get_tile_properties_by_gid(gid)
                            # Проверяем свойство 'collidable' ИЛИ принудительно делаем тайлы 1 и 2 коллайдабельными
                            is_collidable = (props and props.get('collidable', False)) or (gid in {1, 2})

                            # Масштабируем изображение тайла до размера, указанного в TMX
                            scaled_image = pg.transform.scale(tile_image, (self.tile_size, self.tile_size))

                            # Создаем спрайт тайла
                            tile_sprite = Tile(scaled_image, x * self.tile_size, y * self.tile_size)
                            self.tiles.add(tile_sprite)

                            # Если тайл коллайдабельный, добавляем его в соответствующую группу
                            if is_collidable:
                                self.collidable_tiles.add(tile_sprite)

    def run(self, camera) -> None:
        """Отрисовывает видимые тайлы уровня."""
        # Отрисовываем все тайлы через камеру
        for tile in self.tiles:
             self.display_surface.blit(tile.image, camera.apply(tile))