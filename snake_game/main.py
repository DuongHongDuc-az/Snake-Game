import pygame
import sys
from snake.app import Game
from snake.scenes.intro import UI_Manager

# if __name__ == "__main__":
#    Game().run()
#    pygame.quit()
#    sys.exit()

if __name__ == "__main__":
   
 manager = UI_Manager()
 while True:
    manager.run()