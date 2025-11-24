import pygame

class RankingScreen:
    def __init__(self, game=None):
        self.game = game 
        self.font = pygame.font.Font("assets/fonts/Montserrat.ttf", 36)

    def draw(self):
        if not self.game:
            return

        self.game.screen.fill((0, 0, 0))
        title = self.font.render("RANKING - Top 10", True, (255, 255, 0))
        self.game.screen.blit(title, (200, 30))

        if not hasattr(self.game, "ranking_manager"):
            return

        entries = self.game.ranking_manager.get_all()  
        y = 100
        for idx, entry in enumerate(entries[:10], 1): 
            text = f"{idx}. {entry['name']} - {entry['score']} pts - {entry['patente']}"
            surf = self.font.render(text, True, (255, 255, 255))
            self.game.screen.blit(surf, (50, y))
            y += 40

        press = self.font.render("Pressione ENTER para voltar", True, (180, 180, 180))
        self.game.screen.blit(press, (150, 550))
