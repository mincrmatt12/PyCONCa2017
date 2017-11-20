import pygame
import random

class Shape:
    def __init__(self, points=None, color=None):
        self.points = [
            (random.randint(-45, 45), random.randint(-45, 45)) for x in xrange(random.randint(3,8))
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
surface.fill((255, 255, 255))
for i in xrange(12):
    pos_ = random.randint(0, 639), random.randint(0, 479)
    shape = Shape()
    shape.draw(surface, pos_)
    for depth in xrange(3):
        ind = random.randint(0, len(shape.points)-2)
        point_a = shape.points[ind]
        point_b = shape.points[ind+1]
        point_c = random.randint(-60, 60), random.randint(-60, 60 * depth)
        new_s = Shape(points=[point_a, point_b, point_c])
        new_s.draw(surface, pos_)

pygame.image.save(surface, "output/shape.png")