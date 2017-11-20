import pygame
import random
import math

pygame.init()
surf = pygame.Surface([640, 480])

surf.fill((255, 255, 255), (0, 300, 640, 180))
width = random.randint(15, 30)
pos = 300
x = 320 - width/2
top = random.randint(70, 140)

while pos > top:
    height = random.randint(20, 60)
    pos -= height
    color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
    surf.fill(color, (x, pos, width, height))

pygame.image.save(surf, "unity.png")