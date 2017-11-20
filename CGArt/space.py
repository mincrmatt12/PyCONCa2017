import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))

surface = pygame.Surface([1024, 768])
surface.fill(BLACK, [0, 0, 512, 768])
surface.fill(WHITE, [512, 0, 512, 768])


def circle(x, y):
    if random.randint(1, 20) < 2:
        pygame.draw.circle(surface, HIGHLIGHT, (x, y), random.randint(1, 25))
    else:
        if x < 512:
            left_x, left_y = x, y
            right_x = 1024 - x
            right_y = y
        else:
            right_x, right_y = x, y
            left_x = 1024 - x
            left_y = y

        radius = random.randint(3, 15)
        pygame.draw.circle(surface, WHITE, (left_x, left_y), radius)
        pygame.draw.circle(surface, BLACK, (right_x, right_y), radius)


def line(height, coeff, dist, dist2):
    loc = 512

    start = (loc - dist), (height + coeff * dist)
    middle = (loc, height)
    end = (loc + dist), (height + coeff * dist)

    weight = random.randint(1, 5)
    if True:
        pygame.draw.line(surface, WHITE, start, middle, weight)
        pygame.draw.line(surface, BLACK, middle, end, weight)


for i in xrange(50):
    place = random.randint(0, 20)
    if place < 18:
        circle(random.randint(0, 1023), random.randint(0, 767))
    else:
        line(random.randint(20, 890), random.random() * 3 - 1.5, random.randint(50, 500), random.randint(50, 500))

pygame.image.save(surface, "output/space.png")