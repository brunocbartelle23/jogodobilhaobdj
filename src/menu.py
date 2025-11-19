import pygame

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)
        self.font_title.set_bold(True)        
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 40)

        self.bg = pygame.image.load("assets/images/fundomenu.png").convert()
        self.overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        self.overlay.fill((0, 60, 0, 150))

        self.options = ["Iniciar Jogo", f"Dificuldade: {self.game.difficulty.capitalize()}", "Ranking", "Sair"]
        self.selected = 0

        pygame.mixer.music.load("assets/sounds/intro.mp3")
        pygame.mixer.music.play(-1)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.activate_option()
                elif event.key == pygame.K_RIGHT:
                    if self.selected == 1:
                        self.change_difficulty_next()
                elif event.key == pygame.K_LEFT:
                    if self.selected == 1:
                        self.change_difficulty_prev()

    def activate_option(self):
        option = self.options[self.selected]
        if option == "Iniciar Jogo":
            pygame.mixer.music.stop()
            pygame.mixer.Sound("assets/sounds/boasorte.mp3").play()
            self.game.start_quiz()
        elif option.startswith("Dificuldade"):
            self.change_difficulty_next()
        elif option == "Ranking":
            self.game.state = "ranking"
        elif option == "Sair":
            self.game.running = False

    def change_difficulty_next(self):
        if self.game.difficulty == "facil":
            self.game.difficulty = "medio"
            self.options[1] = "Dificuldade: Médio"
        elif self.game.difficulty == "medio":
            self.game.difficulty = "dificil"
            self.options[1] = "Dificuldade: Difícil"
        else:
            self.game.difficulty = "facil"
            self.options[1] = "Dificuldade: Fácil"

    def change_difficulty_prev(self):
        if self.game.difficulty == "facil":
            self.game.difficulty = "dificil"
            self.options[1] = "Dificuldade: Difícil"
        elif self.game.difficulty == "medio":
            self.game.difficulty = "facil"
            self.options[1] = "Dificuldade: Fácil"
        else:
            self.game.difficulty = "medio"
            self.options[1] = "Dificuldade: Médio"

    def draw_button(self, text, x, y, selected=False):
        w, h = 350, 60
        color = (20, 20, 20) if not selected else (10, 120, 10)
        pygame.draw.rect(self.game.screen, color, (x, y, w, h), border_radius=18)
        if selected:
            pygame.draw.rect(self.game.screen, (0, 255, 0), (x, y, w, h), 3, border_radius=18)
        txt = self.font.render(text, True, (255, 255, 255))
        rect = txt.get_rect(center=(x + w // 2, y + h // 2))
        self.game.screen.blit(txt, rect)

    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))
        self.game.screen.blit(self.overlay, (0, 0))
        title = self.font_title.render("SHOW DO MILHÃO", True, (255, 255, 0))
        self.game.screen.blit(title, (110, 70))
        start_y = 230
        for i, option in enumerate(self.options):
            self.draw_button(option, 230, start_y + i * 90, i == self.selected)
