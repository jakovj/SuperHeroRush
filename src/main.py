import pygame
import game
file = 'music.mp3'
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(file)
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.5)

run = True
SuperHeroTower = game.Game()

while run:
    run = SuperHeroTower.startScreen()


pygame.quit()
quit()
