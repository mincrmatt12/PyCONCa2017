import configjson as config
import math


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


class User:
    def __init__(self, pos, camera, geom):
        self.pos = pos
        self.look_at = [0.5, 0.11, 0.5]
        self.camera = camera
        self.mouse_position = [config.window_info.window_size[0] / 2, config.window_info.window_size[1] / 2]
        self.geom_ref = geom
        self.vertical_speed = 0
        self.look_angle = 0

    def update_camera(self):
        self.camera.pos = [self.pos[0], self.pos[1] + 3.375, self.pos[2]]
        factor = 2 * math.pi / config.window_info.window_size[0]
        angle = self.mouse_position[0] * factor
        self.look_angle = angle

        yfactor = 6.0 / config.window_info.window_size[1]
        val = -((self.mouse_position[1] * yfactor) - 3)

        self.camera.look_direction = [math.sin(angle), val, math.cos(angle)]

    def mouse_delta(self, dx, dy):
        self.mouse_position[0] += dx * (config.mouse_sensitivity / 3)
        self.mouse_position[1] += dy * (config.mouse_sensitivity / 3)
        self.mouse_position[0] %= config.window_info.window_size[0]
        self.mouse_position[1] = clamp(0, self.mouse_position[1], config.window_info.window_size[1])

    def physics_tick(self, dx, dz):
        self.vertical_speed -= config.gravity
        self.vertical_speed = max(config.terminal_velocity, self.vertical_speed)
        px, py, pz = self.pos[0] + dx, self.pos[1], self.pos[2] + dz
        for i in self.geom_ref.geoms:
            px, py, pz = i.pushcube.check_and_modify(px, py, pz)
        self.pos = [px, py, pz]
        px, py, pz = self.pos[0], self.pos[1] + self.vertical_speed, self.pos[2]
        for i in self.geom_ref.geoms:
            px, py, pz = i.pushcube.check_and_modify(px, py, pz)
        self.pos = [px, py, pz]
        for i in self.geom_ref.geoms:
            a = i.pushcube.check_and_modify(px, py + 3.375, pz)
            px = a[0]
            pz = a[2]
        self.pos = [px, py, pz]

        if self.pos[1] < -10.0:
            self.pos = [0, 3, 0]
        if self.pos[1] > 250.0:
            self.pos = [0, 3, 0]
            self.vertical_speed /= 2

    def walk_forward(self):
        return self.camera.look_direction[0] * config.walking_speed, self.camera.look_direction[
            2] * config.walking_speed

    def angle_offset(self, angle):
        angle = math.radians(angle)
        return math.sin(self.look_angle + angle) * config.walking_speed, math.cos(
            self.look_angle + angle) * config.walking_speed

    def jump(self):
        self.vertical_speed += config.jump_speed
