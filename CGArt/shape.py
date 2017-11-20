import pygame
import random

class Shape:
    def __init__(self, points=None, color=None):
        self.points = [
            (random.randint(-45, 45), random.randint(-45, 45)) for x in xrange(random.randint(3,4))
        ] if points is None else points
        self.color = pygame.Color(random.choice(pygame.color.THECOLORS.keys())) if color is None else color

    def explode(self, factor):
        return Shape([
            (x[0] * factor, x[1] * factor) for x in self.points
        ], self.color)

    def explode_ip(self, factor):
        self.points = [
            (x[0] * factor, x[1] * factor) for x in self.points
        ]
        return self

    def darken(self, factor):
        self.color = [
            max(0, x * factor) for x in self.color
        ]
        return self

    def draw(self, surf, pos):
        pygame.draw.polygon(surf, self.color, [
            (x[0] + pos[0], x[1] + pos[1]) for x in self.points
        ])

surface = pygame.Surface([640, 480])


def create_drawlist():
    amt = random.randint(8, 15)
    shape = Shape()

    draw_list = [shape]
    for i in xrange(amt):
        draw_list.append(draw_list[-1].explode(1.14).darken(0.89))

    draw_list = list(reversed(draw_list))
    return draw_list

for i in xrange(20):
    pos = (random.randint(0, 640), random.randint(0, 480))
    for j in create_drawlist():
        j.draw(surface, pos)

pygame.image.save(surface, "output/shape.png")