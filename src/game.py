import pygame
import logging
from src.menu import Menu
from src.quiz_manager import QuizManager
from src.cutscene import Cutscene
from src.ranking_manager import RankingManager
from src.ranking_screen import RankingScreen

logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.player_name = "Player"
        self.ranking_manager = RankingManager()
        self.difficulty = "facil"
        self.confirm_sound_played = False
        self.ranking_screen = RankingScreen(game=self)

        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Show do Milhão - Bruno Edition")

        self.player_name = ""  
        self.state = "menu"  
        self.name_input_active = False  
        self.name_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 48)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.menu = Menu(self)
        self.quiz = None
        self.cutscene = None

        self.lives = 3
        self.question_time = 30
        self.time_left = self.question_time
        self.last_tick = pygame.time.get_ticks()

        self.prize_levels = [
            "1 mil", "5 mil", "10 mil", "20 mil",
            "50 mil", "100 mil", "200 mil", "300 mil",
            "500 mil", "1 MILHÃO!!!"
        ]
        self.current_prize = self.prize_levels[0]

        self.score = 0
        self.last_result = None

        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)
        self.big_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)

        self.cooldown_active = False
        self.cooldown_start = 0
        self.cooldown_duration = 5000
        self.last_answer_correct = None
        self.next_question_pending = False

    def start_quiz(self):
        if self.difficulty == "facil":
            self.lives = 3
            self.question_time = 35
        elif self.difficulty == "medio":
            self.lives = 2
            self.question_time = 25
        else:
            self.lives = 1
            self.question_time = 18

        self.time_left = self.question_time
        self.last_tick = pygame.time.get_ticks()

        self.quiz = QuizManager(self)
        self.quiz.start()

    def update_timer(self):
        if self.cooldown_active or self.state == "cutscene":
            return

        now = pygame.time.get_ticks()
        if now - self.last_tick >= 1000:
            self.time_left -= 1
            self.last_tick = now

            if self.time_left <= 0:
                self.lives -= 1
                try:
                    pygame.mixer.Sound("assets/sounds/tempoacabou.mp3").play()
                except:
                    pass

                if self.lives <= 0:
                    self.finish_game(game_over=True)
                else:
                    self.last_answer_correct = False
                    self.cooldown_start = pygame.time.get_ticks()
                    self.cooldown_active = True
                    self.next_question_pending = True

    def finish_game(self, game_over=False):
        self.last_result = {"game_over": game_over}
        if self.quiz:
            total_q = len(self.quiz.questions)
            correct = getattr(self.quiz, "correct_count", 0)
            self.score, patente = Game.compute_score_and_patente(correct, total_q)
            try:
                self.ranking_manager.add_entry(self.player_name, self.score, patente)
            except Exception:
                pass
            self.last_result.update({
                "score": self.score,
                "patente": patente,
                "posicao": self.ranking_manager.get_position(self.player_name, self.score)
            })
        self.state = "fim"

    @staticmethod
    def compute_score_and_patente(correct, total):
        if total <= 0:
            normalized = 0
        else:
            normalized = round((correct / total) * 10)

        if normalized <= 3:
            patente = "Iniciante"
        elif normalized <= 6:
            patente = "Intermediário"
        elif normalized <= 8:
            patente = "Avançado"
        else:
            patente = "Expert"

        return normalized, patente

    def run(self):
        while self.running:
            if self.cooldown_active:
                self.handle_events_during_cooldown()
                self.update_cooldown()
                if self.state == "pergunta" and self.quiz:
                    self.quiz.draw()
                    self.draw_ui()
                elif self.state == "cutscene" and self.cutscene:
                    self.cutscene.draw()
                pygame.display.flip()
                self.clock.tick(60)
                continue

            if self.state == "menu":
                self.menu.update()
                self.menu.draw()
            elif self.state == "input_name":
                self.input_name_screen()
            elif self.state == "cutscene":
                self.cutscene.update()
                self.cutscene.draw()
            elif self.state == "ranking":
                self.ranking_screen.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.state = "menu"
            elif self.state == "pergunta":
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_cooldown(self):
        now = pygame.time.get_ticks()
        if now - self.cooldown_start >= self.cooldown_duration:
            self.cooldown_active = False
            if self.next_question_pending and self.quiz:
                try:
                    self.quiz.next_question(self.last_answer_correct)
                except Exception as e:
                    logger.exception("Erro ao avançar para próxima pergunta: %s", e)
                finally:
                    self.next_question_pending = False

    def draw_ui(self):
        font_big = pygame.font.Font("assets/fonts/Montserrat.ttf", 40)
        font_medium = pygame.font.Font("assets/fonts/Montserrat.ttf", 27)

        timer_text = f"Tempo: {self.time_left}s"
        timer_surf = font_medium.render(timer_text, True, (255, 215, 0))
        timer_bg_w = timer_surf.get_width() + 9
        timer_bg_h = timer_surf.get_height() + 4.5
        timer_bg = pygame.Surface((timer_bg_w, timer_bg_h), pygame.SRCALPHA)
        timer_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(timer_bg, (255, 215, 0), timer_bg.get_rect(), 1, border_radius=8)
        self.screen.blit(timer_bg, (800//2 - timer_bg_w//2, 14))
        self.screen.blit(timer_surf, (800//2 - timer_surf.get_width()//2, 20))

        lives_text = f"Vidas: {self.lives}"
        lives_surf = font_big.render(lives_text, True, (255, 80, 80))
        lives_bg_w = lives_surf.get_width() + 24
        lives_bg_h = lives_surf.get_height() + 12
        lives_bg = pygame.Surface((lives_bg_w, lives_bg_h), pygame.SRCALPHA)
        lives_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(lives_bg, (255, 80, 80), lives_bg.get_rect(), 3, border_radius=12)
        self.screen.blit(lives_bg, (28, 520))
        self.screen.blit(lives_surf, (40, 526))

        prize_text = f"Prêmio: {self.current_prize}"
        prize_surf = font_medium.render(prize_text, True, (0, 255, 120))
        prize_bg_w = prize_surf.get_width() + 24
        prize_bg_h = prize_surf.get_height() + 12
        prize_bg = pygame.Surface((prize_bg_w, prize_bg_h), pygame.SRCALPHA)
        prize_bg.fill((20, 20, 20, 220))
        pygame.draw.rect(prize_bg, (0, 255, 120), prize_bg.get_rect(), 3, border_radius=12)
        self.screen.blit(prize_bg, (800 - prize_bg_w - 28, 520))
        self.screen.blit(prize_surf, (800 - prize_surf.get_width() - 36, 526))

    def update_end_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = "menu"

        self.screen.fill((0, 0, 0))
        msg = ("NÃO DEU PARA VOCÊ!" if self.last_result and self.last_result.get("game_over")
               else "VOCÊ É O MILIONÁRIO!!")
        text = self.big_font.render(msg, True, (255, 255, 0))
        self.screen.blit(text, (100, 200))

        pts = self.font.render(f"Prêmio final: {self.score}", True, (255, 255, 255))
        self.screen.blit(pts, (250, 300))

        press = self.font.render("Pressione ENTER para voltar ao menu.", True, (180, 180, 180))
        self.screen.blit(press, (150, 360))
    def input_name_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.player_name.strip() != "":
                    self.state = "pergunta"
                    self.start_quiz()
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                else:
                    if len(self.player_name) < 12:  
                        self.player_name += event.unicode

        self.screen.fill((0, 0, 0))
        prompt = self.name_font.render("Digite seu nome:", True, (255, 255, 0))
        self.screen.blit(prompt, (180, 150))
        name_surf = self.name_font.render(self.player_name, True, (255, 255, 255))
        self.screen.blit(name_surf, (180, 250))
