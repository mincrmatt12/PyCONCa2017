# OBJLib by mincrmatt12
# Copyright Matthew Mirvish 2016
import os
from OpenGL.GL import *


class OBJFormatError(Exception):
    pass


class OBJ:
    def __init__(self, file_ref):
        self.file_location = file_ref
        self.vertices = {}
        self.vertex_count = 1
        self.texture_coordinates = {}
        self.tex_count = 1
        self.vertex_normals = {}
        self.normal_count = 1
        self.materials = {}
        self.faces = []
        file_ = open(self.file_location, 'r')
        prev = os.getcwd()
        os.chdir(os.path.split(self.file_location)[0])
        self.mtl_file = ""
        self.read(file_.read())
        os.chdir(prev)

    def read_material(self, text):
        processing_material = ""
        for line in text.split("\n"):
            identifiers = line.split(" ")
            if identifiers[0] in ["newmtl", "Kd", "Ka", "Ks", "Ke", "Ns"]:
                identifiers = [x for x in identifiers if x is not '']
            if identifiers[0] == "#":
                continue
            elif identifiers[0] == "newmtl":
                processing_material = " ".join(identifiers[1:])
                self.materials[processing_material] = {}
            elif identifiers[0] == "Kd":
                if processing_material != '':
                    r = float(identifiers[1])
                    g = float(identifiers[2])
                    b = float(identifiers[3])
                    self.materials[processing_material]["diffuse"] = [r, g, b]
            elif identifiers[0] == "Ka":
                if processing_material != '':
                    r = float(identifiers[1])
                    g = float(identifiers[2])
                    b = float(identifiers[3])
                    self.materials[processing_material]["ambient"] = [r, g, b]
            elif identifiers[0] == "Ks":
                if processing_material != '':
                    r = float(identifiers[1])
                    g = float(identifiers[2])
                    b = float(identifiers[3])
                    self.materials[processing_material]["specular"] = [r, g, b]
            elif identifiers[0] == "Ke":
                if processing_material != '':
                    r = float(identifiers[1])
                    g = float(identifiers[2])
                    b = float(identifiers[3])
                    self.materials[processing_material]["emission"] = [r, g, b]
            elif identifiers[0] == "Ns":
                if processing_material != '':
                    s = float(identifiers[1])
                    self.materials[processing_material]["shininess"] = s

    def read(self, text):
        active_material = ""
        for line in text.split("\n"):
            if len(line.strip(" ")) == 0:
                continue
            identifiers = line.split(" ")
            if identifiers[0] in ["v", "vn", "vt", "f", "usemtl", "mtllib"]:
                identifiers = [x for x in identifiers if x is not '']
            if identifiers[0] == "#":
                continue
            elif identifiers[0] == "v":
                x = float(identifiers[1])
                y = float(identifiers[2])
                z = float(identifiers[3])
                self.vertices[self.vertex_count] = [x, y, z]
                self.vertex_count += 1
            elif identifiers[0] == "vn":
                x = float(identifiers[1])
                y = float(identifiers[2])
                z = float(identifiers[3])
                self.vertex_normals[self.normal_count] = [x, y, z]
                self.normal_count += 1
            elif identifiers[0] == "vt":
                u = abs(float(identifiers[1]))
                v = abs(float(identifiers[2]))
                self.texture_coordinates[self.tex_count] = [u, v]
                self.tex_count += 1
            elif identifiers[0] == "mtllib":
                self.read_material(open(" ".join(identifiers[1:]), 'r').read())
                self.mtl_file = " ".join(identifiers[1:])
            elif identifiers[0] == "usemtl":
                mat = " ".join(identifiers[1:])
                if mat not in self.materials:
                    raise OBJFormatError, "Unknown material {}".format(mat)
                else:
                    active_material = mat
            elif identifiers[0] == "f":
                vertex_count = len(identifiers) - 1
                face_data = [active_material, " ".join(identifiers)]
                for i in range(1, vertex_count + 1):
                    vertex = identifiers[i].split("/")
                    pos = [0, 0, 0]
                    uv = [0, 0]
                    normal = [0, 0, 0]
                    textured = False
                    if len(vertex) == 1:
                        pos = self.vertices[int(vertex[0])]
                    elif len(vertex) == 2:
                        pos = self.vertices[int(vertex[0])]
                        uv = self.texture_coordinates[int(vertex[1])]
                        textured = True
                    elif len(vertex) == 3:
                        if vertex[1] != '':
                            pos = self.vertices[int(vertex[0])]
                            uv = self.texture_coordinates[int(vertex[1])]
                            normal = self.vertex_normals[int(vertex[2])]
                            textured = True
                        else:
                            pos = self.vertices[int(vertex[0])]
                            normal = self.vertex_normals[int(vertex[2])]
                            textured = False
                    # noinspection PyTypeChecker
                    face_data.append([pos, uv, normal, textured])
                self.faces.append(face_data)

    def save(self):
        text = ""
        if self.mtl_file != '':
            text += "mtllib " + self.mtl_file + "\n"
        for vertex_ in self.vertices:
            vertex = self.vertices[vertex_]
            text += " ".join(["v"] + [str(x) for x in vertex]) + "\n"
        for normal_ in self.vertex_normals:
            normal = self.vertex_normals[normal_]
            text += " ".join(["vn"] + [str(x) for x in normal]) + "\n"
        for tex_ in self.texture_coordinates:
            tex = self.texture_coordinates[tex_]
            text += " ".join(["vt"] + [str(x) for x in tex]) + "\n"
        current_mtl = ''
        for face in self.faces:
            if current_mtl != face[0]:
                text += "usemtl " + face[0] + "\n"
                current_mtl = face[0]
            text += face[1] + "\n"
        return text

    def compile(self):
        list_id = glGenLists(1)
        texture_enabled = False
        glNewList(list_id, GL_COMPILE)
        glDisable(GL_CULL_FACE)
        glDisable(GL_TEXTURE_2D)
        current_mtl = ''
        for face in self.faces:
            if current_mtl != face[0]:
                if face[0] == '':
                    glEnable(GL_COLOR_MATERIAL)
                    glColor3ub(255, 255, 255)
                else:
                    current_mtl = face[0]
                    glDisable(GL_COLOR_MATERIAL)
                    mtl = self.materials[current_mtl]
                    if 'ambient' in mtl:
                        glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT, mtl['ambient'] + [255])
                    if 'diffuse' in mtl:
                        glMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE, mtl['diffuse'] + [255])
                    if 'specular' in mtl:
                        glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, mtl['specular'] + [255])
                    if 'emission' in mtl:
                        glMaterial(GL_FRONT_AND_BACK, GL_EMISSION, mtl['emission'] + [255])
                    if 'shininess' in mtl:
                        glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, mtl['shininess'])
            if face[2][3] != texture_enabled:
                texture_enabled = face[2][3]
                if face[2][3]:
                    glEnable(GL_TEXTURE_2D)
                else:
                    glDisable(GL_TEXTURE_2D)
            glBegin(GL_POLYGON)
            for vertex in face[2:]:
                glVertex3fv(vertex[0])
                glTexCoord2dv(vertex[1])
                glNormal3fv(vertex[2])
            glEnd()
        glEnable(GL_COLOR_MATERIAL)
        glEndList()
        return list_id
