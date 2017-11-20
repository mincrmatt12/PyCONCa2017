import pygame
import random
pygame.init()

surf = pygame.Surface([3010, 128])

DIST = random.randint(14, 16)
CURVE_COLOR = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))

curve = [[0, 0]]
for i in range(random.randint(4, 8)):
    curve_head = curve[-1]
    move = random.randint(-DIST, DIST), random.randint(0, DIST)
    a = curve_head[0] + move[0], curve_head[1] + move[1]
    curve.append(a)

for x_off in xrange(0, 3010, 256):
    for x in xrange(0, 256, 32):
        pygame.draw.lines(surf, CURVE_COLOR, False, list([(x2[0] + x + x_off, x2[1]) for x2 in curve]), 3)

    for x in xrange(16, 256, 32):
        pygame.draw.lines(surf, CURVE_COLOR, False, list([(x2[0] + x + x_off, 128-x2[1]) for x2 in curve]), 3)

    curve = [[0, 0]]
    for i in range(random.randint(4, 8)):
        curve_head = curve[-1]
        move = random.randint(-DIST, DIST), random.randint(0, DIST)
        a = curve_head[0] + move[0], curve_head[1] + move[1]
        curve.append(a)

pygame.image.save(surf, "repeat.png")