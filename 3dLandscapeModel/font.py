import freetype
import pygame
import math
from OpenGL.GL import *

filtered_printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '


class Font:
    def __init__(self, filename, size):
        # type: (str, int) -> Font
        ftfont = freetype.Face(filename)
        self.size = size
        self.face = ftfont
        self.face.set_char_size(size << 6)
        self.line_height = 0
        self.texture = None
        self.start_list = 0
        self.texture_id = 0
        self.resize()

    def get_char_metrics(self, char):
        self.face.load_char(char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT)

        bitmap = self.face.glyph.bitmap

        lsb = self.face.glyph.bitmap_left
        top = self.face.glyph.bitmap_top
        advance_width = self.face.glyph.advance.x >> 6

        return lsb, top, advance_width

    def resize(self):
        tex_size = int(math.ceil(math.sqrt(len(filtered_printable))) * max((
            (self.face.bbox.xMax >> 6) - (self.face.bbox.xMin >> 6)),
            ((self.face.bbox.yMax >> 6) - (self.face.bbox.yMin >> 6))))

        size_x = ((self.face.bbox.xMax >> 6) - (self.face.bbox.xMin >> 6))
        size_y = ((self.face.bbox.yMax >> 6) - (self.face.bbox.yMin >> 6))

        amt_x = tex_size / size_x
        amt_y = tex_size / size_y

        height = int(math.ceil(len(filtered_printable) / float(amt_x))) * size_y

        self.texture = pygame.Surface([tex_size, height], pygame.SRCALPHA)
        texture2 = pygame.Surface([tex_size, height], pygame.SRCALPHA)

        tex_size_x = float(size_x) / tex_size
        tex_size_y = float(size_y) / height

        x = 0
        y = 0

        metrics_data = {}

        print ("[Font Loader] Loading font with texture {0}x{1}, with {2} glyphs per line, and {3} lines." +
               " Loading 95 glyphs").format(tex_size, height, amt_x, amt_y)

        max_char_height = 0

        for character in filtered_printable:
            self.face.load_char(character, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_FORCE_AUTOHINT)
            data = self.face.glyph.bitmap.buffer
            metrics_data[character] = (
                self.face.glyph.bitmap.width, self.face.glyph.bitmap.rows, float(x) / tex_size, float(y) / height)
            dat_x, dat_y = 0, 0
            for value in data:
                if value < 20:
                    value = 0
                elif value < 255:
                    value = 200
                else:
                    value = 255
                self.texture.set_at((dat_x + x, dat_y + y), (value, value, value, 255 if value > 0 else 0))
                texture2.set_at((dat_x + x, dat_y + y), (value, value, value, 255 if value > 0 else 0))
                if value == 0:
                    self.texture.set_at((dat_x + x, dat_y + y), (0, 0, 0, 255))
                    texture2.set_at((dat_x + x, dat_y + y), (0, 0, 0, 0))
                dat_x += 1
                if dat_x == self.face.glyph.bitmap.width:
                    dat_x = 0
                    dat_y += 1
            x += size_x
            if x >= tex_size:
                x = 0
                y += size_y
            max_char_height = max(max_char_height, self.face.glyph.bitmap.rows)

        self.line_height = max_char_height

        print "[Font Loader] Line height is {}".format(self.line_height)

        print "[Font Loader] Compiling 95 display lists..."

        start = glGenLists(96)

        tex_id = glGenTextures(2)[0]

        data = pygame.image.tostring(self.texture, "RGBA", 0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_size, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        self.start_list = start

        self.texture_id = tex_id

        data = pygame.image.tostring(texture2, "RGBA", 0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id + 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_size, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        for list, char in enumerate(filtered_printable):
            glNewList(start + list, GL_COMPILE)
            lsb, top, advance = self.get_char_metrics(char)
            glBegin(GL_QUADS)
            tex_x = metrics_data[char][2]
            tex_y = metrics_data[char][3]
            glTexCoord2d(tex_x, tex_y)
            glVertex2f(lsb, -top)
            glTexCoord2d(tex_x + tex_size_x, tex_y)
            glVertex2f(lsb + size_x, -top)
            glTexCoord2d(tex_x + tex_size_x, tex_y + tex_size_y)
            glVertex2f(lsb + size_x, (-top) + size_y)
            glTexCoord2d(tex_x, tex_y + tex_size_y)
            glVertex2f(lsb, (-top) + size_y)
            glEnd()
            glTranslate(advance, 0, 0)
            glEndList()

        glNewList(start + 95, GL_COMPILE)
        glPopMatrix()
        glTranslate(0, self.line_height, 0)
        glPushMatrix()
        glEndList()

    def debug_save_texture(self, path):
        pygame.image.save(self.texture, path)

    def text_size(self, text):
        x, y = 0, 0
        x2 = 0
        for character in text:
            if character == '\n':
                x2 = 0
                x = max(x2, x)
                y += self.line_height
            else:
                lsb, top, advance = self.get_char_metrics(character)
                x2 += advance
                print x2
        x = max(x2, x)
        return x, y

    def render(self, text, position, transparent=False):
        lists = [(filtered_printable + "\n").index(x) + self.start_list for x in text]
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id + int(transparent))
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.5)
        glTranslate(position[0], position[1], 0)
        glPushMatrix()
        for list in lists:
            glCallList(list)
        glPopMatrix()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

