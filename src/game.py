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

        # Dificuldade padrão (alterada pelo Menu)
        
        self.difficulty = "facil"
        
        self.confirm_sound_played = False
        
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Show do Milhão - Bruno Edition")

        self.clock = pygame.time.Clock()
        self.running = True

        # estados possíveis: menu, cutscene, pergunta, fim
        self.state = "menu"

        # objetos principais
        self.menu = Menu(self)
        self.quiz = None
        self.cutscene = None

        # sistema de vidas / tentativas (será ajustado em start_quiz)
        self.lives = 3

        # timer da pergunta (ajustado pela dificuldade)
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

        # --- cooldown entre perguntas ---
        self.cooldown_active = False
        self.cooldown_start = 0
        self.cooldown_duration = 5000  # 2.5s de tensão (ajuste se quiser)
        self.last_answer_correct = None
        self.next_question_pending = False  # sinaliza que quiz deve avançar após cooldown

    # ----------------------------------------------------
    def start_quiz(self):
        """Prepara o jogo segundo a dificuldade e inicia o quiz."""
        # Ajusta vidas e tempo por dificuldade
        if self.difficulty == "facil":
            self.lives = 3
            self.question_time = 35
        elif self.difficulty == "medio":
            self.lives = 2
            self.question_time = 25
        else:  # dificil
            self.lives = 1
            self.question_time = 18

        # Reset do timer
        self.time_left = self.question_time
        self.last_tick = pygame.time.get_ticks()

        # Inicializa quiz
        self.quiz = QuizManager(self)
        self.quiz.start()

        # A primeira cutscene é criada pelo QuizManager.start()
        # (se quiser forçar aqui, pode, mas não é necessário)

    # ----------------------------------------------------
    def update_timer(self):
        """Atualiza o timer apenas se não estivermos em cooldown nem em cutscene."""
        # não desconta tempo durante cooldown ou cutscene
        if self.cooldown_active or self.state == "cutscene":
            return

        now = pygame.time.get_ticks()
        if now - self.last_tick >= 1000:
            self.time_left -= 1
            self.last_tick = now

            if self.time_left <= 0:
                # tempo esgotou -> perde vida e toca som
                self.lives -= 1
                try:
                    pygame.mixer.Sound("assets/sounds/tempoacabou.mp3").play()
                except:
                    pass

                if self.lives <= 0:
                    self.finish_game(game_over=True)
                else:
                    # inicia cooldown e marca resultado como incorreto
                    self.last_answer_correct = False
                    self.cooldown_start = pygame.time.get_ticks()
                    self.cooldown_active = True
                    self.next_question_pending = True

    # ----------------------------------------------------
    def finish_game(self, game_over=False):
        self.last_result = {"game_over": game_over}
        self.state = "fim"

    # ----------------------------------------------------
    def run(self):
        while self.running:
            # Processamento de cooldown tem prioridade: trava inputs/updates
            if self.cooldown_active:
                self.handle_events_during_cooldown()
                self.update_cooldown()
                # re-renderiza tela (mantém última tela)
                if self.state == "pergunta" and self.quiz:
                    self.quiz.draw()
                    self.draw_ui()
                elif self.state == "cutscene" and self.cutscene:
                    self.cutscene.draw()
                pygame.display.flip()
                self.clock.tick(60)
                continue

            # Estado normal
            if self.state == "menu":
                self.menu.update()
                self.menu.draw()

            elif self.state == "cutscene":
                # atualiza cutscene; quando cutscene terminar ele define state="pergunta"
                self.cutscene.update()
                self.cutscene.draw()

                # se a cutscene acabou e voltamos pra pergunta, resetamos o timer
                if self.state == "pergunta":
                    self.time_left = self.question_time
                    self.last_tick = pygame.time.get_ticks()

            elif self.state == "pergunta":
                # se o quiz não existe, volta ao menu por segurança
                if not self.quiz:
                    self.state = "menu"
                else:
                    self.update_timer()
                    self.quiz.update()
                    self.quiz.draw()
                    self.draw_ui()

            elif self.state == "fim":
                self.update_end_screen()

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events_during_cooldown(self):
        """Descarta/consome eventos enquanto estiver em cooldown (para evitar inputs indesejados)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # opcional: permitir ESC para pular cooldown em debug (comente em release)
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            #     self.cooldown_active = False

    def update_cooldown(self):
        """Gerencia o fim do cooldown e avança a pergunta se necessário."""
        now = pygame.time.get_ticks()
        if now - self.cooldown_start >= self.cooldown_duration:
            self.cooldown_active = False

            # se quiz existe e há pendência, avança de fato (o QuizManager deve expor o método)
            if self.next_question_pending and self.quiz:
                # delega ao quiz o avanço final
                try:
                    self.quiz.next_question(self.last_answer_correct)
                except Exception as e:
                    logger.exception("Erro ao avançar para próxima pergunta: %s", e)
                finally:
                    self.next_question_pending = False

    # ----------------------------------------------------
    def draw_ui(self):
        """Desenha HUD: tempo (top center), vidas (esq baixo) e prêmio (dir baixo)."""
        # Fonte principal
        font_big = pygame.font.Font("assets/fonts/Montserrat.ttf", 40)
        font_medium = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)

        # --- TEMPO (top center) ---
        timer_text = f"Tempo: {self.time_left}s"
        timer_surf = font_big.render(timer_text, True, (255, 215, 0))
        timer_bg_w = timer_surf.get_width() + 28
        timer_bg_h = timer_surf.get_height() + 14
        timer_bg = pygame.Surface((timer_bg_w, timer_bg_h), pygame.SRCALPHA)
        timer_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(timer_bg, (255, 215, 0), timer_bg.get_rect(), 3, border_radius=12)
        self.screen.blit(timer_bg, (800//2 - timer_bg_w//2, 14))
        self.screen.blit(timer_surf, (800//2 - timer_surf.get_width()//2, 20))

        # --- VIDAS (bottom left) ---
        lives_text = f"Vidas: {self.lives}"
        lives_surf = font_big.render(lives_text, True, (255, 80, 80))
        lives_bg_w = lives_surf.get_width() + 24
        lives_bg_h = lives_surf.get_height() + 12
        lives_bg = pygame.Surface((lives_bg_w, lives_bg_h), pygame.SRCALPHA)
        lives_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(lives_bg, (255, 80, 80), lives_bg.get_rect(), 3, border_radius=12)
        self.screen.blit(lives_bg, (28, 520))
        self.screen.blit(lives_surf, (40, 526))

        # --- PRÊMIO (bottom right) ---
        prize_text = f"Prêmio: {self.current_prize}"
        prize_surf = font_medium.render(prize_text, True, (0, 255, 120))
        prize_bg_w = prize_surf.get_width() + 24
        prize_bg_h = prize_surf.get_height() + 12
        prize_bg = pygame.Surface((prize_bg_w, prize_bg_h), pygame.SRCALPHA)
        prize_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(prize_bg, (0, 255, 120), prize_bg.get_rect(), 3, border_radius=12)
        self.screen.blit(prize_bg, (800 - prize_bg_w - 28, 520))
        self.screen.blit(prize_surf, (800 - prize_surf.get_width() - 36, 526))

    # ----------------------------------------------------
    def update_end_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # volta ao menu (reinicia música do menu, etc.)
                self.state = "menu"
                # opcional: reiniciar menu.music
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
