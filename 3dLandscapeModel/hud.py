from OpenGL.GL import *
from OpenGL.GLU import *
import configjson as config
import font

DEBUG_POSITION = True


class HUD:
    def __init__(self, mdl):
        self.test_font = font.Font("fonts/arial.ttf", 14)
        self.mdl = mdl

    def apply(self, usr):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, *config.window_info.window_size + [0])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.mdl.do_price_labels(self)

        if DEBUG_POSITION:
            glColor3ub(0, 0, 255)
            self.test_font.render("XYZ: {}, {}, {}".format(*usr.pos), [40, 40], True)

        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
