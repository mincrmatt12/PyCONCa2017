import json

from OpenGL.GL import *
from OpenGL.GLU import *

import configjson as config
import objlib
import texture
from collision import PushCube, AABB, point_aabb_distance
from pricelabels import PriceLabels

from cgkit.cgtypes import vec3

geom_data = json.load(open('data.json', 'r'))

_glColor4ubv = glColor4ubv


# noinspection PyPep8Naming
def glColor4ubv(v):
    glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, [x / 255.0 for x in v])
    _glColor4ubv(v)


class Data:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ExtrudeGeom:
    def __init__(self, tag):
        self.position = [0, 0, 0]
        self.size = [0, 0, 0]
        self.points = []
        self.texture_info = None
        self.ref = ""
        self.display_list = None
        self.aabb = None
        self.tex_max_x = 1
        self.tex_max_y = 1
        self.height = 0
        self.vertex_normals = {}
        self.load(tag)
        self.pushcube = PushCube(*self.position + self.size)

    def setup_pointmap(self):
        big_x = -1000
        small_x = 1000
        big_z = -1000
        small_z = 1000
        for point in self.points:
            if point[0] < small_x:
                small_x = point[0]
            if point[1] < small_z:
                small_z = point[1]
            if point[0] > big_x:
                big_x = point[0]
            if point[1] > big_z:
                big_z = point[1]
        self.size = [big_x - small_x, self.height, big_z - small_z]

    def load(self, tag):
        self.ref = tag['ref']
        print "[Extrude Geometry Loader] Loading extrude geometry with ref #{}".format(self.ref)
        self.position = [float(x) for x in tag['position']]
        self.points = tag['points']
        self.height = tag['height']
        self.setup_pointmap()
        self.aabb = AABB(*self.position + self.size)
        if 'texture' in tag:
            self.texture_info = Data(
                color=(255, 255, 255, 255),
                tex_file=tag['texture'],
                sides=[True]
            )
            if 'tex_sides' in tag:
                self.texture_info.sides = tag['tex_sides']
            if 'color' in tag:
                color = tag['color']
                self.texture_info.color = color + [255] if len(color) < 4 else color
        else:
            color = tag['color']
            self.texture_info = Data(
                color=color + [255] if len(color) < 4 else color,
                tex_file='',
                sides=[False for x in range(6)]
            )
        if self.texture_info.tex_file != '':
            self.texture_info.tex_ref = texture.texture[self.texture_info.tex_file]
        if 'wrap' in tag and tag['wrap'] == False:
            self.do_normals()
            return
        self.points.append(self.points[0][:])
        self.do_normals()

    def do_normals(self):
        faces = []
        for pointid in range(len(self.points) - 1):
            a = self.points[pointid]
            b = self.points[pointid + 1]

            va = vec3(a[0], 0 + self.height, a[1])
            vb = vec3(a[0], 0, a[1])
            vc = vec3(b[0], 0 + self.height, b[1])
            vd = vec3(b[0], 0, b[1])

            v1 = va - vb
            v2 = va - vc

            final = v1.cross(v2)
            faces.append(final.normalize())

        faceno = 0

        for pointid in range(len(self.points) - 2):
            a = self.points[pointid]
            b = self.points[pointid + 1]
            c = self.points[pointid + 2]

            normal_a = faces[(faceno - 1) % len(faces)]
            normal_b = faces[faceno]
            normal_c = faces[faceno + 1]
            normal_d = faces[(faceno + 2) % len(faces)]

            vertex_normal_a = normal_a + normal_b
            self.vertex_normals[tuple(a)] = (vertex_normal_a / 2).normalize()

            vertex_normal_b = normal_b + normal_c
            self.vertex_normals[tuple(b)] = (vertex_normal_b / 2).normalize()

            vertex_normal_c = normal_c + normal_d
            self.vertex_normals[tuple(c)] = (vertex_normal_c / 2).normalize()

            faceno += 1

    def setup(self):
        print "[Geometry] [Extrude #{}] Compiling display list...".format(self.ref)
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glPushMatrix()

        glTranslated(*self.position)

        if self.texture_info.sides[0]:
            glEnable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)
            glBindTexture(GL_TEXTURE_2D, self.texture_info.tex_ref)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        tex_increase = self.tex_max_x / float(len(self.points))

        glBegin(GL_QUAD_STRIP)
        for i, point in enumerate(self.points):
            normal = self.vertex_normals[tuple(point)]
            normal_down = vec3(normal.x, -0.5 + normal.y, normal.z).normalize()
            normal_up = vec3(normal.x, 0.5 + normal.y, normal.z).normalize()
            glNormal3fv(list(normal_down))
            glTexCoord2d(tex_increase * i, 0)
            glVertex3f(point[0], 0, point[1])
            glNormal3fv(list(normal_up))
            glTexCoord2d(tex_increase * i, self.tex_max_y)
            glVertex3f(point[0], self.height, point[1])
        glEnd()

        tex_increase_x = self.tex_max_x / float(self.size[0])
        tex_increase_y = self.tex_max_y / float(self.size[1])

        glBegin(GL_POLYGON)
        for point in self.points:
            normal = self.vertex_normals[tuple(point)]
            normal_up = vec3(normal.x, 0.5 + normal.y, normal.z).normalize()
            glNormal3fv(list(normal_up))
            glTexCoord2d(tex_increase_x * point[0], tex_increase_y * point[1])
            glVertex3f(point[0], self.height, point[1])
        glEnd()

        glBegin(GL_POLYGON)
        for point in self.points:
            normal = self.vertex_normals[tuple(point)]
            normal_up = vec3(normal.x, -0.5 + normal.y, normal.z).normalize()
            glNormal3fv(list(normal_up))
            glTexCoord2d(tex_increase_x * point[0], tex_increase_y * point[1])
            glVertex3f(point[0], 0, point[1])
        glEnd()

        glPopMatrix()
        glEndList()

class BoxGeom:
    def __init__(self, tag):
        self.position = [0, 0, 0]
        self.size = [0, 0, 0]
        self.texture_info = None
        self.ref = ""
        self.display_list = None
        self.aabb = None
        self.tex_max_x = 1
        self.tex_max_y = 1
        self.load(tag)
        self.pushcube = PushCube(*self.position + self.size)

    def load(self, tag):
        self.ref = tag['ref']
        print "[Box Geometry Loader] Loading box geometry with ref #{}".format(self.ref)
        self.position = [float(x) for x in tag['position']]
        self.size = [float(x) for x in tag['size']]
        self.aabb = AABB(*self.position + self.size)
        if 'texture' in tag:
            self.texture_info = Data(
                color=(255, 255, 255, 255),
                tex_file=tag['texture'],
                sides=[True for x in range(6)]
            )
            if 'tex_sides' in tag:
                self.texture_info.sides = tag['tex_sides']
            if 'color' in tag:
                color = tag['color']
                self.texture_info.color = color + [255] if len(color) < 4 else color
        else:
            color = tag['color']
            self.texture_info = Data(
                color=color + [255] if len(color) < 4 else color,
                tex_file='',
                sides=[False for x in range(6)]
            )
        if self.texture_info.tex_file != '':
            self.texture_info.tex_ref = texture.texture[self.texture_info.tex_file]
        if 'tex_size' in tag:
            self.tex_max_x, self.tex_max_y = tag['tex_size']

    def setup(self, recompile=False):
        if not recompile:
            print "[Geometry] [Box #{}] Compiling display list".format(self.ref)
            self.display_list = glGenLists(1)
        x, y, z = self.position
        xs, ys, zs = self.size
        glNewList(self.display_list, GL_COMPILE)
        glPushMatrix()
        try:
            glBindTexture(GL_TEXTURE_2D, self.texture_info.tex_ref)
        except AttributeError:
            print "[Geometry] [Box #{}] No texture, this is not an error".format(self.ref)

        if self.texture_info.sides[0]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glVertex3f(x, y + ys, z)
        glNormal3f(-0.57735, 0.57735, -0.57735)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(-0.57735, 0.57735, 0.57735)
        glVertex3f(x, y + ys, z + zs)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(0.57735, 0.57735, 0.57735)
        glVertex3f(x + xs, y + ys, z + zs)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(0.57735, 0.57735, -0.57735)
        glVertex3f(x + xs, y + ys, z)

        glEnd()

        if self.texture_info.sides[1]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glNormal3f(-0.57735, -0.57735, -0.57735)
        glVertex3f(x, y, z)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(-0.57735, -0.57735, 0.57735)
        glVertex3f(x, y, z + zs)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(0.57735, -0.57735, 0.57735)
        glVertex3f(x + xs, y, z + zs)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(0.57735, -0.57735, -0.57735)
        glVertex3f(x + xs, y, z)

        glEnd()

        if self.texture_info.sides[2]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glNormal3f(0.57735, -0.57735, -0.57735)
        glVertex3f(x + xs, y, z)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(0.57735, -0.57735, 0.57735)
        glVertex3f(x + xs, y, z + zs)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(0.57735, 0.57735, 0.57735)
        glVertex3f(x + xs, y + ys, z + zs)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(0.57735, 0.57735, -0.57735)
        glVertex3f(x + xs, y + ys, z)

        glEnd()

        if self.texture_info.sides[3]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glNormal3f(-0.57735, -0.57735, -0.57735)
        glVertex3f(x, y, z)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(-0.57735, -0.57735, 0.57735)
        glVertex3f(x, y, z + zs)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(-0.57735, 0.57735, 0.57735)
        glVertex3f(x, y + ys, z + zs)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(-0.57735, 0.57735, -0.57735)
        glVertex3f(x, y + ys, z)

        glEnd()

        if self.texture_info.sides[4]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glNormal3f(-0.57735, -0.57735, 0.57735)
        glVertex3f(x, y, z + zs)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(-0.57735, 0.57735, 0.57735)
        glVertex3f(x, y + ys, z + zs)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(0.57735, 0.57735, 0.57735)
        glVertex3f(x + xs, y + ys, z + zs)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(0.57735, -0.57735, 0.57735)
        glVertex3f(x + xs, y, z + zs)

        glEnd()

        if self.texture_info.sides[5]:
            glEnable(GL_TEXTURE_2D)
            glColor4ub(255, 255, 255, 255)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor4ubv(self.texture_info.color)

        glBegin(GL_QUADS)

        glTexCoord2d(0, 0)
        glNormal3f(-0.57735, -0.57735, -0.57735)
        glVertex3f(x, y, z)
        glTexCoord2d(0, self.tex_max_y)
        glNormal3f(-0.57735, 0.57735, -0.57735)
        glVertex3f(x, y + ys, z)
        glTexCoord2d(self.tex_max_x, self.tex_max_y)
        glNormal3f(0.57735, 0.57735, -0.57735)
        glVertex3f(x + xs, y + ys, z)
        glTexCoord2d(self.tex_max_x, 0)
        glNormal3f(0.57735, -0.57735, -0.57735)
        glVertex3f(x + xs, y, z)

        glEnd()

        glPopMatrix()

        glEndList()


class OBJGeom:
    def __init__(self, tag):
        self.origin = []
        self.pushcube = None
        self.size = []
        self.translate = []
        self.model = None
        self.ref = ""
        self.texture = ""
        self.display_list = -1
        self.aabb = None
        self.clr = (255, 255, 255)
        self.angle = 0
        self.load(tag)

    def load(self, tag):
        self.ref = tag['ref']
        print "[Geometry] [OBJ] Loading OBJ geometry with ref #{}".format(self.ref)
        self.origin = tag['position']
        model_location = tag['model']
        print "[Geometry] [OBJ #{}] Loading OBJ from {}".format(self.ref, model_location)
        self.model = objlib.OBJ(model_location)
        print "[Geometry] [OBJ #{}] Calculating size...".format(self.ref)
        big_x = -1000
        small_x = 1000
        big_y = -1000
        small_y = 1000
        big_z = -1000
        small_z = 1000
        for vertex_ in self.model.vertices:
            vertex = self.model.vertices[vertex_]
            if vertex[0] > big_x:
                big_x = vertex[0]
            if vertex[0] < small_x:
                small_x = vertex[0]
            if vertex[1] > big_y:
                big_y = vertex[1]
            if vertex[1] < small_y:
                small_y = vertex[1]
            if vertex[2] > big_z:
                big_z = vertex[2]
            if vertex[2] < small_z:
                small_z = vertex[2]
        size_x = big_x - small_x
        size_y = big_y - small_y
        size_z = big_z - small_z

        translate_factor_x = -small_x
        translate_factor_y = -small_y
        translate_factor_z = -small_z

        self.pushcube = PushCube(*self.origin + [size_x, size_y, size_z])
        self.size = [size_x, size_y, size_z]
        self.aabb = AABB(*self.origin + [size_x, size_y, size_z])
        self.translate = [translate_factor_x, translate_factor_y, translate_factor_z]
        if 'texture' in tag:
            self.texture = tag['texture']
        if 'color' in tag:
            self.clr = tag['color']
        if 'angle' in tag:
            self.angle = tag['angle']

    def setup(self):
        model_list = self.model.compile()
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glPushAttrib(GL_LIGHTING_BIT)
        tex_id = -1
        print self.texture
        if self.texture != '':
            tex_id = texture.texture[self.texture]
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
        else:
            tex_id = texture.texture['textures/null.png']
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor3ubv(self.clr)
        glPushMatrix()
        glTranslated(*self.translate)
        glTranslated(*self.origin)
        glRotated(0, 1, 0, self.angle)
        glCallList(model_list)
        glPopMatrix()
        glPopAttrib()
        glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, 25.0)
        glEndList()


geometries = {
    'cube': BoxGeom,
    'obj': OBJGeom,
    'extrude': ExtrudeGeom
}


class StaticModelData:
    def __init__(self):
        self.geoms = []
        self.display_list = 1
        self.load(geom_data)
        self.price_labels = None
        self.label_cache = {}

    def load(self, json_data):
        print "[Model Manager] Loading model 3D data"
        for geom in json_data['geometry']:
            self.geoms.append(geometries[geom['type']](geom))

    def setup(self):
        print "[Model Manager] Compiling mega display list for geometry"
        self.display_list = glGenLists(1)
        print "[Model Manager] Compiling all geometry"
        for geom in self.geoms:
            geom.setup()
        glNewList(self.display_list, GL_COMPILE)
        for geom in self.geoms:
            glCallList(geom.display_list)
        glEndList()
        self.price_labels = PriceLabels(self, geom_data)

    def draw(self):
        glCallList(self.display_list)

    def setup_price_labels(self, user):
        self.label_cache = {}
        for point in self.price_labels.label_data:
            geom = point
            text, point = self.price_labels.label_data[geom]
            try:
                if point_aabb_distance(user.pos, point) > 20:
                    continue
                point = [x + (y / 2) for x, y in zip(point.pos, point.size)]
                x, y, z = gluProject(*point)
                if 0 <= z <= 1:
                    self.label_cache[geom] = [text, (x, config.window_info.window_size[1] - y)]
            except:
                pass

    def do_price_labels(self, hud):
        for geom in self.label_cache:
            text, point = self.label_cache[geom]
            glColor4ub(255, 255, 255, 255)
            hud.test_font.render(text, point)
