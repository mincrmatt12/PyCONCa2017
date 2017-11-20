import pygame
import random
import math

pygame.init()
surf = pygame.Surface([640, 480])
surf.fill((255, 255, 255))

def circle(pos, col=None):
    color = pygame.Color(random.choice(pygame.color.THECOLORS.keys())) if not col else col
    radius = random.randint(3, 15)
    pygame.draw.circle(surf, color, pos, radius)
    return color

for i in xrange(20):
    x = random.randint(100, 200)
    y = random.randint(0, 480)
    x2 = x + 320
    y2 = 480 - y

    col = circle((x, y))
    circle((x2, y2), col)

pygame.image.save(surf, "balance.png")