import pygame

class Menu:
    def __init__(self, game):
        self.game = game

        # ====== FONTE PERSONALIZADA ======
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 50)
        self.font_title = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)
        self.font_title.set_bold(True)
        self.small_font = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)

        # ====== FUNDO DO MENU ======
        self.bg = pygame.image.load("assets/images/fundomenu.png").convert()
        self.bg = pygame.transform.scale(self.bg, (800, 600))

        # ====== OVERLAY VERDE ESCURO 60% ======
        self.overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        self.overlay.fill((0, 60, 0, 150))

        self.options = ["Iniciar Jogo", "Dificuldade: Fácil", "Ranking", "Sair"]
        self.selected = 0

        # ====== TOCAR MÚSICA DE FUNDO ======
        self.tocar_musica_intro()


    def tocar_musica_intro(self):
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/intro.mp3")
        pygame.mixer.music.set_volume(0.6)  # volume opcional
        pygame.mixer.music.play(-1)  # loop infinito


    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                if event.key == pygame.K_RETURN:
                    self.activate_option()


    def activate_option(self):
        option = self.options[self.selected]

        if option == "Iniciar Jogo":
            pygame.mixer.music.stop()
            self.game.start_quiz()

        elif option.startswith("Dificuldade"):
            self.change_difficulty()

        elif option == "Ranking":
            self.game.state = "ranking"

        elif option == "Sair":
            self.game.running = False


    def change_difficulty(self):
        if self.game.difficulty == "facil":
            self.game.difficulty = "medio"
            self.options[1] = "Dificuldade: Médio"

        elif self.game.difficulty == "medio":
            self.game.difficulty = "dificil"
            self.options[1] = "Dificuldade: Difícil"

        else:
            self.game.difficulty = "facil"
            self.options[1] = "Dificuldade: Fácil"


    def draw_button(self, text, x, y, selected=False):
        largura = 350
        altura = 55

        cor = (10, 120, 10) if selected else (20, 20, 20)
        pygame.draw.rect(self.game.screen, cor, (x, y, largura, altura), border_radius=20)

        if selected:
            pygame.draw.rect(self.game.screen, (0, 255, 0), (x, y, largura, altura), width=3, border_radius=20)

        txt = self.small_font.render(text, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(x + largura // 2, y + altura // 2))
        self.game.screen.blit(txt, txt_rect)


    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))
        self.game.screen.blit(self.overlay, (0, 0))

        title = self.font_title.render("SHOW DO MILHÃO", True, (255, 255, 255))
        self.game.screen.blit(title, (155, 65))

        start_y = 200
        spacing = 80

        for i, option in enumerate(self.options):
            self.draw_button(
                option,
                x=230,
                y=start_y + i * spacing,
                selected=(i == self.selected)
            )
