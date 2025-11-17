import pygame
import logging
from src.menu import Menu
from src.quiz_manager import QuizManager
from src.cutscene import Cutscene

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.difficulty="facil"
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Show do Milhão - Bruno Edition")

        self.clock = pygame.time.Clock()
        self.running = True

        # estados possíveis
        self.state = "menu"  # menu, cutscene, pergunta, fim

        # objetos principais
        self.menu = Menu(self)
        self.quiz = None
        self.cutscene = None

        # sistema de vidas / tentativas
        self.lives = 3

        # timer da pergunta
        self.question_time = 30
        self.time_left = self.question_time
        self.last_tick = pygame.time.get_ticks()

        # prêmios
        self.prize_levels = [
            "1 mil", "5 mil", "10 mil", "20 mil",
            "50 mil", "100 mil", "200 mil", "300 mil",
            "500 mil", "1 MILHÃO!!!"
        ]
        self.current_prize = self.prize_levels[0]

        # score final
        self.score = 0
        self.last_result = None

        # fontes
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)
        self.big_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)

    # ----------------------------------------------------
    def start_quiz(self):
    # Ajusta vidas e tempo por dificuldade
        if self.difficulty == "facil":
            self.lives = 3
            self.question_time = 30
        elif self.difficulty == "medio":
            self.lives = 2
            self.question_time = 20
        else:  # dificil
            self.lives = 1
            self.question_time = 15

        self.time_left = self.question_time
        self.last_tick = pygame.time.get_ticks()

        self.quiz = QuizManager(self)
        self.quiz.start()

    # Primeira cutscene
        self.cutscene = Cutscene(self, self.current_prize)
        self.state = "cutscene"


    # Primeira cutscene
        self.cutscene = Cutscene(self, self.current_prize)
        self.state = "cutscene"


    # ----------------------------------------------------
    def update_timer(self):
        now = pygame.time.get_ticks()
        if now - self.last_tick >= 1000:
            self.time_left -= 1
            self.last_tick = now

            if self.time_left <= 0:
                self.lives -= 1
                pygame.mixer.Sound("assets/sounds/errada.mp3").play()

                if self.lives <= 0:
                    self.finish_game(game_over=True)
                else:
                    self.quiz.next_question(correct=False)

    # ----------------------------------------------------
    def finish_game(self, game_over=False):
        self.last_result = {"game_over": game_over}
        self.state = "fim"

    # ----------------------------------------------------
    def run(self):
        while self.running:
            if self.state == "menu":
                self.menu.update()
                self.menu.draw()

            elif self.state == "cutscene":
                self.cutscene.update()
                self.cutscene.draw()

            elif self.state == "pergunta":
                self.update_timer()
                self.quiz.update()
                self.quiz.draw()
                self.draw_ui()

            elif self.state == "fim":
                self.update_end_screen()

            pygame.display.flip()
            self.clock.tick(60)

    # ----------------------------------------------------
    def draw_ui(self):
    # Fonte principal
        font_big = pygame.font.Font("assets/fonts/Montserrat.ttf", 40)
        font_medium = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)

    # --- TEMPO ---
        timer_text = f"Tempo: {self.time_left}s"
        timer_surf = font_big.render(timer_text, True, (255, 215, 0))
        timer_bg = pygame.Surface((timer_surf.get_width()+20, timer_surf.get_height()+10))
        timer_bg.fill((40, 40, 40))
        pygame.draw.rect(timer_bg, (255, 215, 0), timer_bg.get_rect(), 3, border_radius=10)
        self.screen.blit(timer_bg, (800//2 - timer_bg.get_width()//2, 20))
        self.screen.blit(timer_surf, (800//2 - timer_surf.get_width()//2, 25))

    # --- VIDAS ---
        lives_text = f"Vidas: {self.lives}"
        lives_surf = font_big.render(lives_text, True, (255, 80, 80))
        lives_bg = pygame.Surface((lives_surf.get_width()+20, lives_surf.get_height()+10))
        lives_bg.fill((40, 40, 40))
        pygame.draw.rect(lives_bg, (255, 80, 80), lives_bg.get_rect(), 3, border_radius=10)
        self.screen.blit(lives_bg, (50, 520))
        self.screen.blit(lives_surf, (60, 525))

    # --- PRÊMIO ---
        prize_text = f"Prêmio: {self.current_prize}"
        prize_surf = font_medium.render(prize_text, True, (0, 255, 120)) 
        prize_bg = pygame.Surface((prize_surf.get_width()+20, prize_surf.get_height()+10))
        prize_bg.fill((40, 40, 40))
        pygame.draw.rect(prize_bg, (0, 255, 120), prize_bg.get_rect(), 3, border_radius=10)
        self.screen.blit(prize_bg, (800 - prize_bg.get_width() - 50, 520))
        self.screen.blit(prize_surf, (800 - prize_surf.get_width() - 40, 525))


    # ----------------------------------------------------
    def update_end_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = "menu"

        self.screen.fill((0, 0, 0))

        msg = ("NÃO DEU PARA VOCÊ HOJE!"
               if self.last_result and self.last_result.get("game_over")
               else "VOCÊ É O MILIONÁRIO!!")

        text = self.big_font.render(msg, True, (255, 255, 0))
        self.screen.blit(text, (100, 200))

        pts = self.font.render(f"Prêmio final: {self.score}", True, (255, 255, 255))
        self.screen.blit(pts, (250, 300))

        press = self.font.render("Pressione ENTER para voltar ao menu.", True, (180, 180, 180))
        self.screen.blit(press, (150, 360))
