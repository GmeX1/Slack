import pygame
import os
import sys

pygame.init()
pygame.display.set_caption('Slack')
info = pygame.display.Info()
# screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
screen = pygame.display.set_mode((info.current_w - 100, info.current_h - 100))  # На время тестов лучше оконный режим


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Map(pygame.sprite.Sprite):
    img = load_image('test_lvl.png')
    img_mask = load_image('test_lvl_mask.png', (255, 255, 255))

    def __init__(self):
        super().__init__(level_group, all_sprites)
        self.image = Map.img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(Map.img_mask)


if __name__ == '__main__':
    level_group = pygame.sprite.GroupSingle()
    all_sprites = pygame.sprite.Group()

    run = True
    clock = pygame.time.Clock()
    level_test = Map()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        all_sprites.update()
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
