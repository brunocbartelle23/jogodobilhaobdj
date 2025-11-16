import pygame
from src.menu import Menu
from src.quiz_manager import QuizManager
import logging

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Quiz Game")

        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "menu"   # menu, jogando, ranking, fim
        self.menu = Menu(self)

        # dificuldade padrão
        self.difficulty = "facil"

        # quiz manager será criado ao iniciar
        self.quiz = None

        # resultados
        self.score = 0
        self.last_result = None

    def start_quiz(self):
        self.quiz = QuizManager(self)
        self.quiz.start()
        self.state = "jogando"

    def run(self):
        while self.running:
            if self.state == "menu":
                self.menu.update()
                self.menu.draw()

            elif self.state == "jogando":
                if self.quiz:
                    self.quiz.update()
                    self.quiz.draw()

            elif self.state == "fim":
                # tela simples de fim — press enter para voltar ao menu
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # volta ao menu e garante que música do menu toque
                        self.state = "menu"
                        # restart music if menu implements it indirectly
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                self.draw_end_screen()

            elif self.state == "ranking":
                # placeholder: volta ao menu ao pressionar ESC
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                self.screen.fill((0,0,0))
                font = pygame.font.SysFont(None, 36)
                self.screen.blit(font.render("Ranking (ESC para voltar)", True, (255,255,255)), (120, 120))

            pygame.display.flip()
            self.clock.tick(60)

    def draw_end_screen(self):
        self.screen.fill((10,10,10))
        font = pygame.font.SysFont(None, 44)
        small = pygame.font.SysFont(None, 28)
        msg = "NÃO DEU PARA VOCÊ HOJE, VOLTE PARA CASA!" if self.last_result and self.last_result.get("game_over") else "PARABÉNS!"
        self.screen.blit(font.render(msg, True, (255,200,0)), (300, 180))
        self.screen.blit(small.render(f"Pontos: {self.score}", True, (200,255,200)), (350, 260))
        self.screen.blit(small.render("Pressione ENTER para voltar ao menu", True, (180,180,180)), (220, 320))
