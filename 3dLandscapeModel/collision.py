import math

import configjson as config


class AABB:
    def __init__(self, x, y, z, xs, ys, zs):
        self.pos = x, y, z
        self.size = xs, ys, zs

    def point_in_aabb(self, px, py, pz):
        x, y, z = self.pos
        xs, ys, zs = self.size
        if x <= px <= x + xs + 0.05:
            if y <= py <= y + ys:
                if z <= pz <= z + zs + 0.05:
                    return True

        return False


class PushBox:
    def __init__(self, x, y, z, xs, ys, zs, plane):
        self.pos = x, y, z
        self.size = xs, ys, zs
        self.plane = [x, y, z, x + xs, y + ys, z + zs][plane], plane
        self.aabb = AABB(x, y, z, xs, ys, zs)

    def check_and_modify(self, px, py, pz):
        if self.aabb.point_in_aabb(px, py, pz):
            modifier = self.plane[1] % 3
            if modifier == 0:
                px = self.plane[0]
            elif modifier == 1:
                py = self.plane[0]
            elif modifier == 2:
                pz = self.plane[0]
            else:
                print "I don't know whats happening!!"
        return px, py, pz

PUSH_CUBE_WIDTH = 0.25
WALL_DISTANCE = 0.17


class PushCube:
    def __init__(self, x, y, z, xs, ys, zs):
        self.pos = x, y, z
        self.size = xs, ys, zs
        print "[Collision] Generating pushbox at {}, {}, {} size {}x{}x{}".format(x, y, z, xs, ys, zs)
        self.pushboxes = []
        self.gen_pushboxes()

    def debug_pushcube(self):
        for c in self.pushboxes:
            print c.pos, c.size, c.plane

    def add_pushbox(self, x, y, z, xs, ys, zs, plane):
        self.pushboxes.append(PushBox(x, y, z, xs, ys, zs, plane))

    def gen_pushboxes(self):
        x, y, z = self.pos
        xs, ys, zs = self.size
        self.add_pushbox(x, y + ys - PUSH_CUBE_WIDTH, z, xs, WALL_DISTANCE + PUSH_CUBE_WIDTH, zs, 4)
        self.add_pushbox(x - WALL_DISTANCE, y, z, PUSH_CUBE_WIDTH + WALL_DISTANCE, ys, zs, 0)
        self.add_pushbox((x + xs) - PUSH_CUBE_WIDTH, y, z, PUSH_CUBE_WIDTH + WALL_DISTANCE, ys, zs, 3)
        self.add_pushbox(x, y, z - WALL_DISTANCE, xs, ys, PUSH_CUBE_WIDTH + WALL_DISTANCE, 2)
        self.add_pushbox(x, y, (z + zs) - PUSH_CUBE_WIDTH, xs, ys, PUSH_CUBE_WIDTH + WALL_DISTANCE, 5)

    def check_and_modify(self, px, py, pz):
        for i in self.pushboxes:
            px, py, pz = i.check_and_modify(px, py, pz)
        return px, py, pz


def point_aabb_distance(b, a):
    cx = max(min(b[0], a.pos[0] + a.size[0]), a.pos[0])
    cy = max(min(b[1], a.pos[1] + a.size[1]), a.pos[1])
    cz = max(min(b[2], a.pos[2] + a.size[2]), a.pos[2])
    return math.sqrt((b[0] - cx)**2 + (b[1] - cy)**2 + (b[2] - cz)**2)