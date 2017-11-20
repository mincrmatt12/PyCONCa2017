import objlib

a = objlib.OBJ(raw_input())
for vertex_ in a.vertices:
    vertex = a.vertices[vertex_]

    vertex[0] *= 0.1
    vertex[1] *= 0.1
    vertex[2] *= 0.1

    a.vertices[vertex_] = vertex
f = open('models/bbq.obj', 'w')
f.write(a.save())
f.close()
