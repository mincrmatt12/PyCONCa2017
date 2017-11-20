import pygame
import random
import math

pygame.init()
surf = pygame.Surface([640, 480])
surf.fill((255, 255, 255))


class Tri:
    def __init__(self):
        self.pos = (10, random.randint(0, 480))
        self.color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
        self.percent = 1.0
        self.size = 15
        self.surf_ = pygame.Surface([30, 30], pygame.SRCALPHA)
        self.surf_.fill((0,0,0,0))

    def update(self):
        col = 255 - self.color.r * self.percent, 255 - self.color.g * self.percent, 255 - self.color.b * self.percent
        pygame.draw.polygon(self.surf_, col, ([0, 0], [15, 15], [0, 30]))

    def move(self):
        total_dist = 640
        fact = self.percent / 1.2
        self.percent = fact
        move_by = total_dist * fact
        self.pos = [640 - move_by, self.pos[1]]

    def draw(self):
        surf.blit(self.surf_, self.pos)

for i in xrange(20):
    t = Tri()
    for j in xrange(15):
        t.update()
        t.draw()
        t.move()

pygame.image.save(surf, "move.png")