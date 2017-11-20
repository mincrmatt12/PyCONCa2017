import configjson as config
import pygame

HELD_KEY = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]


class InputHandler:
    def __init__(self, user):
        self.held_keys = []
        self.user = user
        self.dx_move = 0
        self.dz_move = 0

    def single_keypress(self, key):
        if key == pygame.K_SPACE:
            self.user.jump()
        elif key == pygame.K_ESCAPE:
            raise

    def held_key(self, key):
        if key == pygame.K_w:
            self.dx_move, self.dz_move = self.user.walk_forward()
        elif key == pygame.K_s:
            self.dx_move, self.dz_move = [-x for x in self.user.walk_forward()]
        elif key == pygame.K_a:
            self.dx_move, self.dz_move = self.user.angle_offset(90)
        elif key == pygame.K_d:
            self.dx_move, self.dz_move = self.user.angle_offset(-90)

    def key_down(self, event):
        if event.key in HELD_KEY:
            self.held_keys.append(event.key)
        else:
            self.single_keypress(event.key)

    def key_up(self, event):
        if event.key in self.held_keys:
            self.held_keys.remove(event.key)

    def game_loop(self):
        self.dx_move, self.dz_move = 0, 0
        for i in self.held_keys:
            self.held_key(i)

    def mouse_move(self, event):
        dx = -(event.pos[0] - config.window_info.window_size[0] / 2)
        dy = event.pos[1] - config.window_info.window_size[1] / 2
        self.user.mouse_delta(dx, dy)
        pygame.mouse.set_pos(config.window_info.window_size[0] / 2, config.window_info.window_size[1] / 2)

    def dispatch(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event)
        elif event.type == pygame.KEYUP:
            self.key_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_move(event)
