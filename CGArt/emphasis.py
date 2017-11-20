import pygame
import random
import math

pygame.init()
surf = pygame.Surface([640, 480])

ccolor = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
mcolor = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
fcolor = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))


for i in xrange(320):
    x, y = random.randint(0, 639), random.randint(0, 479)

    distance = math.sqrt(((x - 320) + (y - 240))**2)
    if distance < (240 if y > 280 else 160):
        if distance < 40:
            size = random.randint(6, 18)
            surf.fill(ccolor, (
                x - size, y - size, size, size
            ))
        elif distance < 90:
            radius = random.randint(3, 8)
            pygame.draw.circle(surf, mcolor, (x, y), radius)
        else:
            surf.fill(fcolor, (x, y, 1, 1))

pygame.image.save(surf, "emphasis.png")
