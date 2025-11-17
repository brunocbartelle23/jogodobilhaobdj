import pygame
import time

class Cutscene:
    def __init__(self, game, premio="1 mil"):
        self.game = game
        self.start_time = time.time()
        self.duration = 3  # duração em segundos

        self.font_title = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)
        self.font_title.set_bold(True)
        self.small_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 35)

        # overlay preto
        self.overlay = pygame.Surface((800, 600))
        self.overlay.fill((0, 0, 0))

        # texto
        self.texto = f"Valendo {premio} reais!"

        # som
        try:
            pygame.mixer.Sound("assets/sounds/boasorte.mp3").play()
        except:
            print("⚠ Som boasorte.mp3 não encontrado")

    def update(self):
        if time.time() - self.start_time >= self.duration:
            if self.game.lives > 0:
                self.game.state = "pergunta"

            # **reset do timer da pergunta**
                self.game.time_left = self.game.question_time
                self.game.last_tick = pygame.time.get_ticks()
            else:
                self.game.finish_game(game_over=True)

    def draw(self):
        self.game.screen.blit(self.overlay, (0, 0))
        title = self.font_title.render(self.texto, True, (255, 255, 0))
        rect = title.get_rect(center=(400, 260))
        self.game.screen.blit(title, rect)

        sub = self.small_font.render("Prepare-se...", True, (255, 255, 255))
        sub_rect = sub.get_rect(center=(400, 340))
        self.game.screen.blit(sub, sub_rect)
