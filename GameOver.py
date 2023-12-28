import pygame
class GameOverScreen:
    def __init__(self, screen, player_time, enemies_killed):
        self.screen = screen
        self.player_time = player_time
        self.enemies_killed = enemies_killed
        self.font = pygame.font.Font(None, 36)

    def show_screen(self):
        game_over_text = self.font.render("Game Over", True, (255, 0, 0))
        time_text = self.font.render(f"Time: {self.player_time} seconds", True, (255, 255, 255))
        enemies_text = self.font.render(f"Enemies Killed: {self.enemies_killed}", True, (255, 255, 255))

        self.screen.blit(game_over_text, (250, 200))
        self.screen.blit(time_text, (250, 250))
        self.screen.blit(enemies_text, (250, 300))

        pygame.display.flip()
