import pygame
from sys import exit

pygame.init()

screen_x = 600
screen_y = 800
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("LavaEscape!")
clock = pygame.Clock()
game_active = True

background = pygame.image.load("graphics/Background/Blue.png")

lcliff_surf = pygame.image.load("graphics/Tiles/stoneCliffLeft.png").convert_alpha()
rcliff_surf = pygame.image.load("graphics/Tiles/stoneCliffRight.png").convert_alpha()
mcliff_surf = pygame.image.load("graphics/Tiles/stoneMid.png").convert_alpha()

player_surf = pygame.image.load("graphics/Main Characters/Ninja Frog/Idle (32x32).png").convert_alpha()
player_surf.
player_rect = player_surf.get_rect(center = (300, 300))

def displayBackground():
    for x in range(int(screen_x / background.get_width())+1):
        for y in range(int(screen_y / background.get_height())+1):
            screen.blit(background, (background.get_width() * (x), background.get_height() * (y)))

def drawLevel():
    rect_list = []
    rect_list.append(pygame.draw.rect(screen, (255,255,255), (0, 700, 250, 100)))
    rect_list.append(pygame.draw.rect(screen, (255,255,255), (350, 500, 250, 100)))
    rect_list.append(pygame.draw.rect(screen, (255,255,255), (0, 300, 250, 100)))
    rect_list.append(pygame.draw.rect(screen, (255,255,255), (350, 100, 250, 100)))
    rect_list.append(pygame.draw.rect(screen, (255,255,255), (0, 700, 250, 100)))
    for rect in rect_list:
        screen.blit(screen, rect, rect)
    return rect_list

def drawPlayer():
    screen.blit(player_surf, player_rect)


while game_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((0,0,0))
    displayBackground()
    drawLevel()
    drawPlayer()

    pygame.display.update()
    clock.tick(60)
