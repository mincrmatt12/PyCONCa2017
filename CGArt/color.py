import pygame
import random
import noise
import copy

squares = []
for x in xrange(0, 3010, 40):
    for y in xrange(0, 256, 40):
        squares.append((
            (x, y), (x+40, y), (x+40, y+40)
        ))
        squares.append((
            (x, y), (x, y + 40), (x+40, y + 40)
        ))

better_squares = []


def screw_with(position):
    offset_x = random.randint(-15, 15)
    offset_y = random.randint(-15, 15)

    return position[0] + offset_x, position[1] + offset_y

screwed_with = {}

for index in range(len(squares)):
    new_pos = []
    for pos in squares[index]:
        poss_new = screw_with(pos[:])
        if pos in screwed_with:
            poss_new = screwed_with[pos]
        else:
            screwed_with[pos] = poss_new
        new_pos.append(poss_new)
    color = pygame.Color("black")
    color.hsla = (squares[index][0][0] / 3010.0 * 360, 50, min(256, squares[index][0][1] + 20) / 256.0 * 100)
    better_squares.append((color, new_pos))

pygame.init()
surf = pygame.Surface([3010, 256])
for better_tri in better_squares:
    color, tri = better_tri
    pygame.draw.polygon(surf, color, tri)

pygame.image.save(surf, "color.png")
