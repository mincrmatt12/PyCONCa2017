import pygame
import random
import math
import noise

SEED = random.randint(0, 9999) / 10000.0

pygame.init()
# debug
surf = pygame.Surface([640, 480])
surf.fill((255, 255, 255))
color = tuple(pygame.Color(random.choice(pygame.color.THECOLORS.keys())))

for i in xrange(1020):
    x, y = random.randint(0, 639), random.randint(0, 479)
    radius = random.randint(3, 25)

    value = min(abs(noise.snoise3(SEED, x/(640.0*1.5), y/(480.0*1.5))), 1.0)
    if value < 0.05:
        value *= 2
    color_ = list(color)
    color_[0] *= value
    color_[1] *= value
    color_[2] *= value
    color_[3] = 255

    pygame.draw.circle(surf, color_, (x, y), radius)

pygame.image.save(surf, "value.png")
