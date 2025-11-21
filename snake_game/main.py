import pygame
import sys
from snake.app import Game
from   snake.scenes.intro  import Button,UI

if __name__ == "__main__":
    ui=UI()
    game=Game()
    result = ui.run()
    if result == 1:
        game.run()
    else :
     pygame.quit()
     sys.exit()