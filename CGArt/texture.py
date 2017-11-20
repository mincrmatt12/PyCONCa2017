import pygame
import random
import noise
import copy
import matplotlib.path as paths

squares = []
for x in xrange(0, 1024, 40):
    for y in xrange(0, 768, 40):
        squares.append((
            (x, y), (x+40, y), (x+40, y+40), (x, y+40)
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
        poss_new = screw_with(pos)
        if pos in screwed_with:
            poss_new = screwed_with[pos]
        else:
            screwed_with[pos] = poss_new
        new_pos.append(poss_new)
    color = random.choice(pygame.color.THECOLORS.keys())
    while color == "black":
        color = random.choice(pygame.color.THECOLORS.keys())
    better_squares.append((pygame.Color(color), new_pos))

pygame.init()


def fuzz_inside(quantity, poly, color):
    path = paths.Path(poly)
    bbox = path.get_extents()
    x0, x1 = bbox.xmin, bbox.xmax
    y0, y1 = bbox.ymin, bbox.ymax

    success = 0
    while success < quantity:
        x = random.randint(x0, x1)
        y = random.randint(y0, y1)
        if path.contains_point((x, y)):
            success += 1
            surf.fill(color, (x, y, 2, 2))

surf = pygame.Surface([1024, 768])
for better_tri in better_squares:
    color, tri = better_tri
    fuzz_inside(random.randint(50, 200), tri, color)

pygame.image.save(surf, "texture.png")
