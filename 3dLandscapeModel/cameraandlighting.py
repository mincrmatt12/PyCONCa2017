from OpenGL.GL import *
from OpenGL.GLU import *
import configjson as config
import texture


class Light:
    used_lights = 0

    def __init__(self, position, ambient, diffuse, specular):
        if Light.used_lights > 8:
            raise Exception, "Attempt to create more than 8 lights"
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.lightid = Light.used_lights
        Light.used_lights += 1
        glEnable(eval("GL_LIGHT" + str(self.lightid)))

    def apply(self):
        glLightfv(eval("GL_LIGHT" + str(self.lightid)), GL_AMBIENT, self.ambient)
        glLightfv(eval("GL_LIGHT" + str(self.lightid)), GL_DIFFUSE, self.diffuse)
        glLightfv(eval("GL_LIGHT" + str(self.lightid)), GL_SPECULAR, self.specular)
        glLightfv(eval("GL_LIGHT" + str(self.lightid)), GL_POSITION, self.position)


class CameraAndLighting:
    def __init__(self):
        self.pos = [-5.5, 2.15, -5.5]
        self.look_direction = [0.5, 0.11, 0.5]
        self.lights = [Light((-5, 20, -5), (.3, .3, .3, 0), (1, 1, 1, 1), (1, 1, 1, 1)),
                       Light((30, 20, 64), (.2, .2, .2, 0), (1, 1, 1, 1), (1, 1, 1, 1))]

    def setup(self):
        print "[Main] Setting up display stuffies"  # Yes pycharm, stuffies is a word.
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_BLEND)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glClearColor(*config.clear_color)
        glViewport(0, 0, *config.window_info.window_size)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(config.window_info.fov, config.window_info.window_size[0] / config.window_info.window_size[1],
                       0.1, 250.0)

        glMaterial(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
        glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, (1, 1, 1, 1))
        glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, 25.0)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def apply(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(config.window_info.fov, config.window_info.window_size[0] / config.window_info.window_size[1],
                       0.1, 250.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        for light in self.lights:
            light.apply()
        look_at = [x + y for x, y in zip(self.pos, self.look_direction)]
        gluLookAt(*self.pos + look_at + [0, 1, 0])
