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
        self.await_confirm = False
        self.answer_selected = None

    # ---------------------------------------------------------
    # INÍCIO DO QUIZ
    # ---------------------------------------------------------
    def start(self):
        self.load_questions()
        self.current_index = 0
        self.current_question = self.questions[0]
        self.game.current_prize = self.game.prize_levels[0]
        
        # Cutscene inicial
        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    # ---------------------------------------------------------
    # CARREGAR QUESTÕES
    # ---------------------------------------------------------
    def load_questions(self):
        with open("data/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.questions = [
            Question(q["pergunta"], q["opcoes"], q["resposta"])
            for q in data
        ]

    # ---------------------------------------------------------
    # TRATAR RESPOSTA
    # ---------------------------------------------------------
    def answer(self, index):
        correct = (index == self.current_question.correct_index)

        # Toca som IMEDIATAMENTE
        try:
            if correct:
                pygame.mixer.Sound("assets/sounds/certaresposta.mp3").play()
            else:
                pygame.mixer.Sound("assets/sounds/errou.mp3").play()
        except:
            pass

        # Inicia cooldown
        self.game.cooldown_start = pygame.time.get_ticks()
        self.game.cooldown_active = True
        self.game.last_answer_correct = correct

        # Aguarda o cooldown para ir pra próxima
        self.next_question(correct)

    # ---------------------------------------------------------
    # PRÓXIMA PERGUNTA
    # ---------------------------------------------------------
    def next_question(self, correct):
        if not correct:
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.finish_game(game_over=True)
                return

        # Avança no array
        self.current_index += 1

        # Final do quiz
        if self.current_index >= len(self.questions):
            self.game.finish_game(game_over=False)
            return

        self.current_question = self.questions[self.current_index]
        self.game.current_prize = self.game.prize_levels[self.current_index]

        # Mostra cutscene da nova pergunta
        self.game.cutscene = Cutscene(self.game, self.game.current_prize)
        self.game.state = "cutscene"

    # ---------------------------------------------------------
    # CONTROLES & INPUT
    # ---------------------------------------------------------
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            # SELEÇÃO DA RESPOSTA (1-4)
            if event.type == pygame.KEYDOWN and not self.await_confirm:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    self.answer_selected = event.key - pygame.K_1
                    self.await_confirm = True
                    self.confirm_sound_played = False
                    return

            # CONFIRMAÇÃO
            if self.await_confirm and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.await_confirm = False
                    self.answer(self.answer_selected)
                    return

                # ESC = cancelar
                elif event.key == pygame.K_ESCAPE:
                    self.await_confirm = False
                    self.answer_selected = None
                    return

    # ---------------------------------------------------------
    # DESENHO DA TELA DO QUIZ
    # ---------------------------------------------------------
    def draw(self):
        self.game.screen.fill((0, 0, 50))

        pergunta = self.font.render(
            self.current_question.text,
            True,
            (255, 255, 255)
        )
        self.game.screen.blit(pergunta, (40, 60))

        # Opções
        for i, opcao in enumerate(self.current_question.options):
            cor = (200, 200, 0)
            txt = self.font.render(f"{i+1}) {opcao}", True, cor)
            self.game.screen.blit(txt, (100, 180 + i * 70))

        # CONFIRMAÇÃO
        if self.await_confirm:
            if not self.confirm_sound_played:
                pygame.mixer.Sound("assets/sounds/certeza.mp3").play()
                self.confirm_sound_played = True

            self.draw_confirmation()

    # ---------------------------------------------------------
    # TELA: "VOCÊ TEM CERTEZA?"
    # ---------------------------------------------------------
    def draw_confirmation(self):
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.game.screen.blit(overlay, (0, 0))

        font_big = pygame.font.Font("assets/fonts/Montserrat.ttf", 50)
        font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)
        txt = font_big.render("Você tem certeza?", True, (255, 255, 0))
        self.game.screen.blit(txt, (180, 150))

        opt1 = font.render("ENTER = Sim", True, (0, 255, 0))
        self.game.screen.blit(opt1, (260, 300))

        opt2 = font.render("ESC = Não", True, (255, 80, 80))
        self.game.screen.blit(opt2, (260, 360))
