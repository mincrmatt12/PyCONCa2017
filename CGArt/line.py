import pygame
import random
import math


class Ball:
    def __init__(self, pos, vel):
        self.pos = pos
        self.last = pos
        self.vel = vel
        self.weight = random.randint(1, 4)
        self.color = pygame.Color(random.choice(pygame.color.THECOLORS.keys()))
        self.restart = 0
        self.do_draw = True
        self.hit = False

    def update(self):
        self.last = self.pos[:]
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[1] > 480:
            self.pos[1] = 480
            self.vel[1] = -self.vel[1]
            if not self.hit:
                self.vel[1] /= 1.09
            else:
                self.vel[1] = min(self.vel[1], -(random.random() * 10))
                self.hit = False

        if abs(self.vel[0]) < 0.025:
            self.vel[0] = 0
        if self.pos[0] < 0 or self.pos[0] > 640:
            self.vel[0] = -self.vel[0]
        else:
            self.vel[0] += math.copysign(0.015, -self.vel[0])
        if abs(self.vel[1]) < 0.00025:
            self.vel[1] = 0
        else:
            self.vel[1] += 0.15

    def draw(self, surf):
        if ball.do_draw:
            pygame.draw.line(surf, self.color, self.last, self.pos, self.weight)


balls = []
for i in range(400):
    pos = [random.randint(5, 635), random.randint(2, 498)]
    vel = [random.randint(-5, 5), random.random() + 0.1 if random.randint(0, 5) in [0, 1] else -(random.random()*5)]

    balls.append(Ball(pos, vel))

pygame.init()
# debug
surf = pygame.display.set_mode([640, 480])
clock = pygame.time.Clock()
surf.fill((255, 255, 255))
for frame in xrange(1040):
    # surf.fill((255, 255, 255))
    clock.tick(60)

    pygame.event.pump()
    for ball in balls:
        ball.update()
        if abs(ball.vel[0]) < 0.05:
            ball.vel = [random.randint(-6, 6), ball.vel[1]]
            ball.restart += 1
            ball.hit = True
            if ball.restart > 1:
                ball.do_draw = False
        if ball.do_draw:
            ball.draw(surf)
    pygame.display.flip()

pygame.image.save(surf, "output/line.png")
