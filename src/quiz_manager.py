import pygame
import json
import random
import time
import logging
from src.question import Question  # se tiver, senão o Question é simples dict

logger = logging.getLogger(__name__)

class QuizManager:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        # fontes (usa Montserrat já no projeto)
        try:
            self.title_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 36)
            self.opt_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 28)
        except Exception:
            # fallback
            self.title_font = pygame.font.SysFont(None, 36)
            self.opt_font = pygame.font.SysFont(None, 28)

        # estado do quiz
        self.questions = []
        self.current_idx = 0
        self.total_questions = 5
        self.score = 0
        self.pergunta_start_ms = 0

        # opções de layout para botões de resposta
        self.option_rects = []
        self.feedback = None  # ("certo"/"errado", timestamp)
        self.load_questions()

        # configurações por dificuldade (serão definidas no start)
        self.time_limit = 20
        self.tries = 1

    def load_questions(self):
        try:
            with open("data/questions.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # filtra entradas válidas
            data = [q for q in data if "pergunta" in q and "opcoes" in q and "resposta" in q]
            random.shuffle(data)
            self.questions = data[:self.total_questions]
        except Exception as e:
            logger.exception("Erro ao carregar perguntas")
            self.questions = []

    def start(self):
        # aplicar dificuldade definida no game
        diff = getattr(self.game, "difficulty", "facil")
        if diff == "facil":
            self.tries = 3
            self.time_limit = 30
        elif diff == "medio":
            self.tries = 1
            self.time_limit = 20
        else:
            self.tries = 0
            self.time_limit = 15

        self.current_idx = 0
        self.score = 0
        self.player_tries = self.tries
        self.pergunta_start_ms = pygame.time.get_ticks()
        self.feedback = None
        # preparar rects para as opções
        self.prepare_option_rects()

    def prepare_option_rects(self):
        # calcula retângulos em tela para 4 opções (2x2)
        w, h = self.screen.get_size()
        btn_w, btn_h = 320, 60
        left = (w - btn_w) // 2
        top = 220
        spacing = 80
        self.option_rects = []
        for i in range(4):
            x = left
            y = top + i * (btn_h + 10)
            self.option_rects.append(pygame.Rect(x, y, btn_w, btn_h))

    def get_current(self):
        if 0 <= self.current_idx < len(self.questions):
            return self.questions[self.current_idx]
        return None

    def update(self):
        # eventos básicos (fecha janela)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                self.handle_click(mx, my)

        # atualizar timer
        now = pygame.time.get_ticks()
        elapsed = (now - self.pergunta_start_ms) / 1000.0
        if elapsed >= self.time_limit:
            # tempo esgotado: considerar como erro
            self.on_wrong("Tempo esgotado")
            return

        # limpar feedback antigo após 0.8s
        if self.feedback and (now - self.feedback[1]) > 800:
            self.feedback = None

    def handle_click(self, mx, my):
        # verifica se clicou numa opção
        for idx, rect in enumerate(self.option_rects):
            if rect.collidepoint(mx, my):
                self.answer(idx)
                break

    def answer(self, idx):
        q = self.get_current()
        if q is None:
            return

        correct_idx = q["resposta"]
        # algumas perguntas podem ter menos de 4 opcoes, proteção
        if idx >= len(q["opcoes"]):
            return

        # checa resposta
        if idx == correct_idx:
            self.on_correct()
        else:
            self.on_wrong(f"Errado (opção {idx})")

    def on_correct(self):
        # pontos: 100 base + bônus por tempo restante
        now = pygame.time.get_ticks()
        elapsed = (now - self.pergunta_start_ms) / 1000.0
        bonus = max(0, int((self.time_limit - elapsed) * 10))  # exemplo
        self.score += 100 + bonus
        self.feedback = ("certo", pygame.time.get_ticks())
        # avançar para próxima pergunta
        self.current_idx += 1
        if self.current_idx >= len(self.questions):
            self.finish_quiz()
            return
        self.pergunta_start_ms = pygame.time.get_ticks()
        # reset tentativas ao mudar de pergunta
        self.player_tries = self.tries

    def on_wrong(self, reason="Errado"):
        # penalidade: perde uma tentativa (se tinha), senão game over
        if self.player_tries > 0:
            self.player_tries -= 1
            self.feedback = ("errado", pygame.time.get_ticks())
            # reinicia o tempo da mesma pergunta
            self.pergunta_start_ms = pygame.time.get_ticks()
        else:
            # sem tentativas: game over
            self.feedback = ("errado", pygame.time.get_ticks())
            self.finish_quiz(game_over=True)

    def finish_quiz(self, game_over=False):
        # salva resultado no game para tela final ou ranking posterior
        self.game.score = self.score
        self.game.last_result = {"game_over": game_over, "question_idx": self.current_idx}
        self.game.state = "fim"

    def draw(self):
        screen = self.screen
        screen.fill((10, 10, 40))

        q = self.get_current()
        if q is None:
            # sem perguntas -> volta ao menu
            info = self.title_font.render("Sem perguntas disponíveis", True, (255, 100, 100))
            screen.blit(info, (120, 250))
            return

        # desenha pergunta (com quebra simples)
        wrap_lines = self.wrap_text(q["pergunta"], self.title_font, 700)
        y = 60
        for line in wrap_lines:
            surf = self.title_font.render(line, True, (255, 255, 255))
            screen.blit(surf, (40, y))
            y += surf.get_height() + 6

        # desenha opções
        for i, option_text in enumerate(q["opcoes"]):
            if i >= len(self.option_rects):
                break
            rect = self.option_rects[i]
            # cor do botão depende do feedback
            base = (255,255,255)
            if self.feedback and (self.feedback[0] == "certo") and i == q["resposta"]:
                base = (150, 255, 150)
            elif self.feedback and (self.feedback[0] == "errado") and i != q["resposta"]:
                # se houve erro mostre vermelho no botão errado selecionado (não sabemos qual foi clicado aqui),
                # então apenas marca o certo em verde e mantém os demais brancos
                base = (255,255,255)
            pygame.draw.rect(screen, base, rect, border_radius=12)
            # contorno
            pygame.draw.rect(screen, (30,30,30), rect, width=2, border_radius=12)
            # texto centralizado
            txt = self.opt_font.render(option_text, True, (0,0,0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

        # desenha timer e tentativas e pontuação
        now = pygame.time.get_ticks()
        elapsed = (now - self.pergunta_start_ms) / 1000.0
        time_left = max(0, int(self.time_limit - elapsed))
        timer_surf = self.opt_font.render(f"Tempo: {time_left}s", True, (255,255,0))
        screen.blit(timer_surf, (600, 30))

        tries_surf = self.opt_font.render(f"Tentativas: {self.player_tries}", True, (255,200,200))
        screen.blit(tries_surf, (40, 30))

        score_surf = self.opt_font.render(f"Pontos: {self.score}", True, (200,255,200))
        screen.blit(score_surf, (320, 30))

        # se feedback, mostrar mensagem
        if self.feedback:
            txt = "ACERTOU!" if self.feedback[0] == "certo" else "ERRADO!"
            color = (0,200,0) if self.feedback[0] == "certo" else (200,0,0)
            fb_surf = self.title_font.render(txt, True, color)
            screen.blit(fb_surf, (520, 520))

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
