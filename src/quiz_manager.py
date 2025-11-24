import pygame
import json
from src.question import Question
from src.cutscene import Cutscene

class QuizManager:
    def __init__(self, game):
        self.game = game
        self.questions = []
        self.current_index = 0
        self.current_question = None
        self.bg = pygame.image.load("assets/images/fundomenu.png").convert()
        self.bg = pygame.transform.scale(self.bg, (800, 600))
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)
        self.font.set_bold(True)

        self.await_confirm = False
        self.answer_selected = None
        self.confirm_sound_played = False
        self.correct_count = 0
        self.selected_option = 0

    def start(self):
        self.load_questions()
        self.current_index = 0
        self.current_question = self.questions[0]
        self.correct_count = 0

        self.game.current_prize = self.game.prize_levels[0]
        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    def load_questions(self):
        with open("data/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.questions = [
            Question(q["pergunta"], q["opcoes"], q["resposta"])
            for q in data
        ]

    def answer(self, index):
        correct = (index == self.current_question.correct_index)

        try:
            if correct:
                self.correct_count += 1
                if self.current_index < len(self.game.prize_levels):
                    self.game.current_prize = self.game.prize_levels[self.current_index]
                pygame.mixer.Sound("assets/sounds/certaresposta.mp3").play()
            else:
                pygame.mixer.Sound("assets/sounds/errou.mp3").play()
        except:
            pass

        self.game.cooldown_start = pygame.time.get_ticks()
        self.game.cooldown_active = True
        self.game.last_answer_correct = correct

        self.next_question(correct)

    def next_question(self, correct):
        if not correct:
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.score = 0
                self.game.finish_game(game_over=True)
                return

        self.current_index += 1

        if self.current_index >= len(self.questions):
            prize_values = [1000, 5000, 10000, 20000, 50000, 100000, 200000, 300000, 500000, 1000000]
            self.game.score = prize_values[min(self.correct_count, len(prize_values)-1)]
            self.game.finish_game(game_over=False)
            return

        self.current_question = self.questions[self.current_index]
        self.game.current_prize = self.game.prize_levels[self.current_index]
        self.selected_option = 0

        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if not self.await_confirm and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.current_question.options)
                    return
                if event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.current_question.options)
                    return
                if event.key == pygame.K_RETURN:
                    self.answer_selected = self.selected_option
                    self.await_confirm = True
                    self.confirm_sound_played = False
                    return

            if self.await_confirm and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.await_confirm = False
                    self.answer(self.answer_selected)
                    return
                elif event.key == pygame.K_ESCAPE:
                    self.await_confirm = False
                    self.answer_selected = None
                    return

    def draw_text_wrap(self, text, font, color, x, y, max_width, line_height):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        for i, line in enumerate(lines):
            txt_surf = font.render(line, True, color)
            self.game.screen.blit(txt_surf, (x, y + i * line_height))

    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))
        self.draw_text_wrap(self.current_question.text, self.font, (255, 255, 255), 40, 60, 720, 40)
        self.draw_option_buttons()

        if self.await_confirm:
            if not self.confirm_sound_played:
                pygame.mixer.Sound("assets/sounds/certeza.mp3").play()
                self.confirm_sound_played = True
            self.draw_confirmation()

    def draw_option_buttons(self):
        for i, opcao in enumerate(self.current_question.options):
            selected = (self.selected_option == i)

            bg_color = (70, 70, 130) if not selected else (255, 200, 0)
            text_color = (255, 255, 255) if not selected else (0, 0, 0)

            box = pygame.Rect(80, 180 + i * 90, 640, 70)
            pygame.draw.rect(self.game.screen, bg_color, box, border_radius=15)

            if selected:
                pygame.draw.rect(self.game.screen, (255, 255, 255), box, 4, border_radius=15)

            txt = self.font.render(f"{opcao}", True, text_color)
            self.game.screen.blit(txt, (100, 195 + i * 90))

    def draw_confirmation(self):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.game.screen.blit(overlay, (0, 0))

        font_big = pygame.font.Font("assets/fonts/Montserrat.ttf", 50)
        font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)

        txt = font_big.render("Você tem certeza?", True, (255, 255, 0))
        self.game.screen.blit(txt, (170, 150))

        opt1 = font.render("ENTER = Sim", True, (0, 255, 0))
        self.game.screen.blit(opt1, (260, 300))

        opt2 = font.render("ESC = Não", True, (255, 80, 80))
        self.game.screen.blit(opt2, (260, 360))
