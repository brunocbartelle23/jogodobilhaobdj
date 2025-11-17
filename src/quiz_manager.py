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
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)

    def start(self):
        self.load_questions()
        self.current_index = 0
        self.current_question = self.questions[0]
        self.game.current_prize = self.game.prize_levels[0]

        # Primeira cutscene
        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    def load_questions(self):
        with open("data/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.questions = [Question(q["pergunta"], q["opcoes"], q["resposta"]) for q in data]

    def answer(self, index):
        correct = (index == self.current_question.correct_index)
        try:
            if correct:
                pygame.mixer.Sound("assets/sounds/certaresposta.mp3").play()
            else:
                pygame.mixer.Sound("assets/sounds/errou.mp3").play()
        except:
            pass

        self.next_question(correct)

    def next_question(self, correct):
        if not correct:
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.finish_game(game_over=True)
                return

        # Avança
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.game.finish_game(game_over=False)
            return

        self.current_question = self.questions[self.current_index]
        self.game.current_prize = self.game.prize_levels[self.current_index]

        # Inicia cutscene antes da próxima pergunta
        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    self.answer(event.key - pygame.K_1)

    def draw(self):
        self.game.screen.fill((0, 0, 50))
        pergunta = self.font.render(self.current_question.text, True, (255, 255, 255))
        self.game.screen.blit(pergunta, (40, 60))

        for i, opcao in enumerate(self.current_question.options):
            txt = self.font.render(f"{i+1}) {opcao}", True, (200, 200, 0))
            self.game.screen.blit(txt, (100, 180 + i * 70))
