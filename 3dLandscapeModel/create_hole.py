posx = int(raw_input("X1> "))
posy = int(raw_input("X2> "))
height_pos = int(raw_input("Y> "))

sizex = int(raw_input("SX> "))
sizey = int(raw_input("SY> "))
height_size = int(raw_input("HS> "))

holex = int(raw_input("HX> "))
holey = int(raw_input("HY> "))

holesx = int(raw_input("HSX> "))
holesy = int(raw_input("HSY> "))

ref = raw_input("REF> ")
tex = raw_input("TEX> ")

fmt = """{{
    "type": "cube",
    "position": [
        {},
        {},
        {}
    ],
    "size": [
        {},
        {},
        {}
    ],
    "ref": "{}",
    "texture": "{}"
}},
"""

print fmt.format(posx, height_pos, posy, holex, height_size, holey + holesy, ref + "1", tex)
print fmt.format(posx + holex + holesx, height_pos, posy + holey, sizex - (holex + holesx), height_size,
                 sizey - holey, ref + "2", tex)

print fmt.format(posx + holex, height_pos, posy, sizex - holex, height_size, holey, ref + "3", tex)
print fmt.format(posx, height_pos, posy + holesy + holey, sizex - holex, height_size, sizey - holey - holesy,
                 ref + "4", tex)
