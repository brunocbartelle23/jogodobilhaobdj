import pygame
import logging
import os
from src.game import Game

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "game.log"), encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging configurado e iniciado.")

def main():
    setup_logging()
    
    logging.info("Iniciando o Pygame...")
    pygame.init()
    
    logging.info("Criando instância do Jogo.")
    game = Game()
    game.run()
    
    logging.info("Jogo finalizado. Encerrando Pygame.")
    pygame.quit()

if __name__ == "__main__":
    main()