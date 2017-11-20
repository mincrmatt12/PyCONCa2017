import pygame
import random
import math

pygame.init()
surf = pygame.Surface([1024, 768])

def circle(pos):
    color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
    radius = random.randint(3, 15)
    pygame.draw.circle(surf, color, pos, radius)


def square(pos):
    color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
    width = random.randint(5, 15)
    degree = random.randint(0, 180)
    surf_ = pygame.Surface([width*2, width*2])
    surf_.fill(color, (0, 0, width, width))
    surf.blit(pygame.transform.rotate(surf_, degree), pos)


def triangle(pos):
    color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
    width = random.randint(20, 30)
    degree = random.randint(0, 180)
    surf_ = pygame.Surface([width, width])

    p1 = [0, width]
    p2 = [width/2, width/2]
    p3 = [width, width]

    pygame.draw.polygon(surf_, color, (p1, p2, p3))
    surf.blit(pygame.transform.rotate(surf_, degree), pos)

for i in xrange(240):
    t = random.randint(0, 2)
    pos = random.randint(0, 1024), random.randint(0, 768)
    if t == 0:
        circle(pos)
    elif t == 1:
        square(pos)
    else:
        triangle(pos)

pygame.image.save(surf, "variety.png")
