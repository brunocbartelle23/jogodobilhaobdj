import pygame

class RankingScreen:
    def __init__(self, game, ranking_manager):
        self.game = game
        self.ranking_manager = ranking_manager
        self.font_title = pygame.font.Font("assets/fonts/Montserrat.ttf", 60)
        self.font_title.set_bold(True)
        self.font_entry = pygame.font.Font("assets/fonts/Montserrat.ttf", 32)
        self.bg_color = (10, 10, 50)
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 215, 0)

    def draw(self):
        self.game.screen.fill(self.bg_color)

        # Título
        title_surf = self.font_title.render("RANKING", True, self.highlight_color)
        title_rect = title_surf.get_rect(center=(400, 80))
        self.game.screen.blit(title_surf, title_rect)

        # Lista de entradas
        entries = self.ranking_manager.get_all()  # deve retornar lista de dicts com 'name', 'score', 'patente'
        for i, entry in enumerate(entries[:10]):  # top 10
            y = 150 + i * 40
            text = f"{i+1}. {entry['name']} - {entry['score']} ({entry['patente']})"
            entry_surf = self.font_entry.render(text, True, self.text_color)
            self.game.screen.blit(entry_surf, (100, y))

        # Instrução
        instr_surf = self.font_entry.render("Pressione ENTER para voltar ao menu", True, (180, 180, 180))
        instr_rect = instr_surf.get_rect(center=(400, 550))
        self.game.screen.blit(instr_surf, instr_rect)

