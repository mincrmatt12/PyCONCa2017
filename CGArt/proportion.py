import pygame
import random
import math

pygame.init()
surf = pygame.Surface([640, 480])

color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))

for i in xrange(320):
    x, y = random.randint(0, 639), random.randint(0, 479)

    size = int((32.0 / 480) * y)/2
    print x-size, y-size, x+size, y+size
    surf.fill(color, (
        x-size, y-size, size, size
    ))

pygame.image.save(surf, "prop.png")