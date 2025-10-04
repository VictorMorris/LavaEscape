import pygame
from sys import exit
import player
import level
import menu

pygame.init()

screen = pygame.display.set_mode((400, 800))
pygame.display.set_caption("LavaEscape!")
clock = pygame.Clock()
game_active = True

while game_active:
    pygame.display.update()
    clock.tick(60)
