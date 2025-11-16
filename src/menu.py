import pygame

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont("Arial", 50)
        self.small_font = pygame.font.SysFont("Arial", 35)

        # Opções do menu
        self.options = ["Iniciar Quiz", "Ranking", "Opções", "Sair"]
        self.selected = 0  # qual opção o cursor está apontando

    def update(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:

                # mover seta para cima
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                # mover seta para baixo
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                # ENTER → confirma a opção
                if event.key == pygame.K_RETURN:
                    self.execute_option()

    def execute_option(self):
        option = self.options[self.selected]

        if option == "Iniciar Quiz":
            self.game.state = "jogando"

        elif option == "Ranking":
            self.game.state = "ranking"

        elif option == "Opções":
            self.game.state = "opcoes"

        elif option == "Sair":
            self.game.running = False

    def draw(self):
        self.game.screen.fill((40, 40, 40))

        title = self.font.render("QUIZ GAME", True, (255,255,255))
        self.game.screen.blit(title, (260, 80))

        # desenhar as opções
        for i, option in enumerate(self.options):
            if i == self.selected:
                color = (255, 200, 0)
                prefix = "> "
            else:
                color = (255, 255, 255)
                prefix = "  "

            text = self.small_font.render(prefix + option, True, color)
            self.game.screen.blit(text, (280, 220 + i*60))
