import pygame
import random
import math

pygame.init()
surf = pygame.Surface([1024, 768])
surf.fill((255, 255, 255))

color1 = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
color2 = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
color3 = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
color4 = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))

colors = [color1, color2, color3, color4]


def quad(pos):
    if pos[0] < 512:
        if pos[1] > 384:
            return 1
        else:
            return 0
    else:
        if pos[1] > 384:
            return 2
        else:
            return 3


def circle():
    pos = random.randint(0, 1024), random.randint(0, 768)
    radius = random.randint(10, 30)
    center = (512, 384)
    color = colors[quad(pos)]
    pygame.draw.circle(surf, color, pos, radius)
    pygame.draw.line(surf, (0, 0, 0), pos, center, 3)

for i in xrange(64):
    circle()

pygame.image.save(surf, "contrast.png")