import pygame
from OpenGL.GL import *


def load_texture(tex):
    print "[Texture Manager] Loading texture from {}".format(tex)

    new_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, new_id)

    pygame_surf = pygame.image.load(tex)
    image_data = pygame.image.tostring(pygame_surf, "RGBA", 1)

    width = pygame_surf.get_width()
    height = pygame_surf.get_height()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return new_id


class Textures:
    def __init__(self):
        self.textures = {}

    def __setitem__(self, key, value):
        pass

    def __getitem__(self, item):
        if item in self.textures:
            return self.textures[item]
        else:
            self.textures[item] = load_texture(item)
            return self.textures[item]


texture = Textures()
