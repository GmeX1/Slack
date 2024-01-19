from UI_class import UI
from init import *
from menu_class import DeathScreen, Menu, Pause
from music_class import Music
from player_class import Enemy, Player
from scripts import generate_tiles, show_fps, time_convert
from small_logic_classes import Level


def start_game(level_name):
    all_sprites.empty()
    player_group.empty()
    enemies.empty()
    camera.empty()

    level = Level(level_name, camera, screen)
    player = Player(level.get_player_spawn(),
                    False)  # TODO: Переделать, тесты (level.get_story_mode())
    camera.get_map_image(level.image)

    if level.get_enemies_pos():
        [Enemy(i, player) for i in level.get_enemies_pos()]

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
                    player.cur_frame = 0
                    player.step_frame = 1
                    if player.last_keys == 1:
                        player.last_anim = 'shoot_r'
                        player.update_anim('shoot_r')
                    elif player.last_keys == -1:
                        player.last_anim = 'shoot_l'
                        player.update_anim('shoot_l')
                    shoot_timer = pygame.time.get_ticks()
                if event.button == 1 and not player.dashing:
                    player.cur_frame = 0
                    player.step_frame = 1
                    if player.last_keys == 1:
                        player.last_anim = 'punch_r'
                        player.update_anim('punch_r')
                    elif player.last_keys == -1:
                        player.last_anim = 'punch_l'
                        player.update_anim('punch_l')
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and player.last_anim.startswith('punch'):
                    player.last_anim = ''

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music.pause()
                    pygame.mixer.pause()
                    pause.set_last_frame()
                    menu_open = pause.start()
                    if menu_open:
                        pygame.mixer.stop()
                        pygame.mixer.music.unload()
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
            death_screen.set_last_frame()
            death_screen.set_stats(player.kills, time_convert(pygame.time.get_ticks()))
            music.pause()
            pygame.mixer.fadeout(150)
            menu_open = death_screen.start()
            pygame.mixer.fadeout(150)
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
        if level.switch_trigger:
            if level.get_exit_rect().colliderect(player.rect):
                if len(enemies) == 0:
                    menu.show_loading()
                    return 'next'
                print('не все мертвы')
        ui.draw()

        music.check_combo(player.combo)

        if fps_switch:
            show_fps(screen, clock)
        pygame.display.flip()
        clock.tick(100)
    pygame.quit()
    return False


if __name__ == '__main__':
    stats = {
        'level': 1
    }
    ui = UI()
    menu = Menu()
    pause = Pause()
    death_screen = DeathScreen()
    menu.start()
    generate_tiles()
    music = Music()
    answer = start_game('1')
    while answer:
        if answer == 'menu':
            menu.start()
            music = Music()
        if answer == 'restart':
            ui = UI()
            death_screen = DeathScreen()
            music = Music()
        if answer == 'next':
            stats['level'] += 1
        answer = start_game(str(stats['level']))
