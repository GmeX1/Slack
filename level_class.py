import os
import pygame
from converter import split_image
from tile_class import Tile


class Level:
    def __init__(self, image, level_name, surface):
        self.image = image
        self.pos = (0, 0)
        self.surface = surface
        self.tiles = pygame.sprite.Group()

        if not os.path.isfile(os.path.join(*['data', 'maps'], f'{level_name}.tiles')):
            # text = pygame.font.SysFont('Times New Roman', 100, True)
            # render = text.render('ЗАГРУЗКА...', True, (255, 0, 0))
            # self.surface.blit(
            #    render,
            #    (surface.get_width() / 2 - render.get_width() / 2, surface.get_height() / 2 - render.get_height() / 2))
            # TODO: Из-за того, что подгрузка тайлов происходит в ините, кадр не обновляется и таблички с загрузкой
            #  не видно. Нужно как-то переработать механизм так, чтобы можно было визуально оповестить о создании тайлов

            rects = split_image(f'data/maps/{level_name}_mask.png')
            open(f'data/maps/{level_name}.tiles', mode='w').write(str(rects))
        else:
            rects = eval(open(f'data/maps/{level_name}.tiles', mode='r').read())
        [Tile(i[0], *i[1], self.tiles) for i in rects]

    def update(self):
        # self.surface.blit(self.image, self.pos)  # Если надо отрисовать карту
        self.tiles.draw(self.surface)  # Если надо отрисовать сами тайлы

