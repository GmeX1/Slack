import sys

from init import *
from UI_class import UI
from menu_class import DeathScreen, Menu, Pause
from player_class import Bullet, Enemy, Player
from scripts import generate_tiles, show_fps, time_convert
from small_logic_classes import Camera, Level
from music_class import Music

pygame.display.set_caption('Slack')
info = pygame.display.Info()
# screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
screen = pygame.display.set_mode((info.current_w - 100, info.current_h - 100))  # На время тестов лучше оконный режим

# TODO: переписать код, чтобы классы активно пользовались init.py
def load_image(name, colorkey=None):  # TODO: Перенести функцию в scripts
    path = ['data']
    if '\\' in name:
        [path.append(i) for i in name.split('\\')]
    else:
        path.append(name)
    fullname = os.path.join(*path)

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


def start_game(level_name):
    bullet_icon = load_image('bullet\\bullet.png')

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_group = pygame.sprite.GroupSingle()
    camera = Camera(screen)

    level = Level(load_image(f'maps\\{level_name}.png'), level_name, screen, camera)
    music = Music(level_name)
    player = Player(load_image('player\\idle\\idle_r.png'), level.get_player_spawn(),
                    True,  # TODO: Переделать, тесты (level.get_story_mode())
                    all_sprites, camera, player_group)
    player.import_anims(load_image)
    camera.get_map_image(level.image)

    # [Enemy(pygame.Surface((10, 50)), i, player, bullet_icon,
    #        all_sprites, enemies, camera) for i in level.get_enemies_pos()]

    cur = db.cursor()
    fps_switch = cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]

    ui.set_hp(player.hp)

    run = True
    clock = pygame.time.Clock()
    shoot_timer = pygame.time.get_ticks()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and pygame.time.get_ticks() - shoot_timer > 500 and player.collisions['bottom']:
                    if player.last_keys == 1:
                        player.last_anim = 'shoot_r'
                        player.update_anim('shoot_r')
                    elif player.last_keys == -1:
                        player.last_anim = 'shoot_l'
                        player.update_anim('shoot_l')
                    Bullet(bullet_icon, (player.map_rect.centerx,player.map_rect.centery - 20 ), player.last_keys, 'player',
                           all_sprites, camera)
                    shoot_timer = pygame.time.get_ticks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music.pause()
                    pause.set_last_frame(screen.copy())
                    menu_open = pause.start()
                    if menu_open:
                        return 'menu'
                    fps_switch = cur.execute(f'SELECT value FROM settings WHERE name="show_fps"').fetchall()[0][0]
                    music.update_volume()
                    music.resume()
                if event.key == pygame.K_q:
                    ui.activate_rage()
                if event.key == pygame.K_h:  # TODO: Убрать. Для тестов.
                    if player.hp > 0:
                        player.hp -= 1
                        ui.remove_hp()
                if event.key == pygame.K_j:
                    ui.kill(100)
        all_sprites.update(tiles=level.tiles, enemies=enemies, player=player_group)
        screen.fill((0, 0, 0))
        camera.draw_offset(player)

        # Синхронизация действий игрока с UI
        if player.hp < ui.hp_amount:
            ui.remove_hp()
        if player.hp <= 0:
            death_screen.set_last_frame(screen.copy())
            death_screen.set_stats(player.kills, time_convert(pygame.time.get_ticks()))
            menu_open = death_screen.start()
            if menu_open:
                return 'menu'
            else:
                return 'restart'
        if player.kills > ui.kills:
            ui.kill(50)  # TODO: Сделать коэффициент
        if ui.combo_timer:
            if player.combo != ui.combo:
                player.combo = ui.combo
                death_screen.max_combo = max(ui.combo, death_screen.max_combo)
        else:
            player.combo = 0
        if ui.deplete:
            player.raging = True
        else:
            player.raging = False
        ui.draw()

        music.check_combo(player.combo)

        if fps_switch:
            show_fps(screen, clock)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
    return False


if __name__ == '__main__':
    ui = UI(screen, screen.get_size(), load_image)
    menu = Menu(screen, db)
    pause = Pause(screen, db)
    death_screen = DeathScreen(screen, db)
    menu.start()
    generate_tiles()
    answer = start_game('1')
    while answer:
        if answer == 'menu':
            menu.start()
        ui = UI(screen, screen.get_size(), load_image)
        death_screen = DeathScreen(screen, db)
        answer = start_game('1')  # Пока что игра просто перезапускается, ибо нет контрольных точек
