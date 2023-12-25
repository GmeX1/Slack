import os
import pygame
from scripts import split_image
from tile_class import Tile


class Level:
    def __init__(self, image, level_name, surface, camera):
        self.image = image
        self.surface = surface
        self.tiles = pygame.sprite.Group()

        # Подгрузка тайлов из файла имя_карты.tiles, либо свежая генерация с последующим сохранением в файл.
        # Синим цветом на маске обозначена точка спавна игрока.
        # Жёлтым цветом на маске обозначен режим игры (сюжетный или основной)
        if not os.path.isfile(os.path.join(*['data', 'maps'], f'{level_name}.tiles')):
            print('По какой-то причине тайлы отсутствуют, генерация...')
            rects = split_image(f'data/maps/{level_name}_mask.png')
            open(f'data/maps/{level_name}.tiles', mode='w').write(str(rects))
        else:
            rects = eval(open(f'data/maps/{level_name}.tiles', mode='r').read())
        self.player_spawn_pos = rects.pop(rects.index(list(filter(lambda x: x[0] == (0, 0, 255, 255), rects))[0]))
        self.player_spawn_pos = self.player_spawn_pos[1][:2]

        # Режим карты, необходим для определения переключателя ходьба/бег у игрока
        self.story_mode = list(filter(lambda x: x[0] == (255, 255, 0, 255), rects))
        if self.story_mode:
            rects.pop(rects.index(self.story_mode[0]))
            self.story_mode = True
        else:
            self.story_mode = False

        [Tile(i[0], *i[1], self.tiles, camera) for i in rects]

    def get_story_mode(self):
        return self.story_mode

    def get_player_spawn(self):
        return self.player_spawn_pos


class Camera(pygame.sprite.Group):
    def __init__(self, surface):
        super().__init__()
        self.surface = surface
        self.offset = pygame.math.Vector2(0, 0)
        self.maximum = (float('inf'), float('inf'))
        self.map_image = None
        self.map_rect = None
        self.borders = {
            'left': self.surface.get_width() / 6,
            'right': self.surface.get_width() / 6 * 5,
            'top': self.surface.get_height() / 6,
            'bottom': self.surface.get_height() / 6 * 5
        }
        self.pos_rect = pygame.Rect(
            self.borders['left'],
            self.borders['top'],
            self.borders['right'] - self.borders['left'],
            self.borders['bottom'] - self.borders['top']
        )

    def set_max(self, maximum):
        self.maximum = maximum

    def get_map_image(self, image):
        self.map_image = image
        self.map_rect = self.map_image.get_rect()

    def draw_offset(self, player):
        if player.map_rect.left < self.pos_rect.left:
            self.pos_rect.left = player.map_rect.left
        elif player.map_rect.right > self.pos_rect.right:
            self.pos_rect.right = player.map_rect.right

        if player.map_rect.top < self.pos_rect.top:
            self.pos_rect.top = player.map_rect.top
        elif player.map_rect.bottom > self.pos_rect.bottom:
            self.pos_rect.bottom = player.map_rect.bottom

        if self.maximum[0] - self.borders['left'] < self.pos_rect.right:
            self.pos_rect.right = self.maximum[0] - self.borders['left']
        if self.maximum[1] - self.borders['top'] < self.pos_rect.bottom:
            self.pos_rect.bottom = self.maximum[1] - self.borders['top']

        self.offset.x = self.pos_rect.left - self.borders['left']
        self.offset.y = self.pos_rect.top - self.borders['top']

        if self.offset.x < 0:
            self.offset.x = 0
        if self.offset.y < 0:
            self.offset.y = 0

        if self.map_image:
            pos = self.map_rect.topleft - self.offset
            self.surface.blit(self.map_image, pos)

        for sprite in self.sprites():
            if hasattr(sprite, 'map_rect'):
                pos = sprite.map_rect.topleft - self.offset
            else:
                pos = sprite.rect.topleft - self.offset
            if sprite.__class__ != Tile:
                self.surface.blit(sprite.image, pos)
