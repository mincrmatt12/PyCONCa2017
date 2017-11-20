import scripting

import texture
import collision


def logger(text):
    print "[Script] [Logger] {}".format(text)


class ScriptHolder:
    def __init__(self, mdl, usr):
        self.mdl = mdl
        self.usr = usr
        self.require_texture = scripting.BuiltinFunction("RequireTexture", 1, lambda x: texture.texture[x])
        self.object_get_distance = scripting.BuiltinFunction("ObjectDistanceFromPlayer", 1,
                                                             self.object_distance_from_player)
        self.box_set_texture2 = scripting.BuiltinFunction("BoxSetTexture", 2, self.box_set_texture)
        self.evaluator = scripting.Evaluator(logger)
        funcs = {}
        for f in [self.require_texture, self.object_get_distance, self.box_set_texture2]:
            name = f.name
            funcs[name] = f
        self.evaluator.functions.update(funcs)

    def box_set_texture(self, ref, tex):
        box = [x for x in self.mdl.geoms if x.ref == ref][0]
        box.texture_info.tex_ref = tex
        box.setup(True)

    def object_distance_from_player(self, ref):
        object_aabb = [x for x in self.mdl.geoms if x.ref == ref][0].aabb
        return collision.point_aabb_distance(self.usr.pos, object_aabb)

    def player_moves(self):
        self.evaluator.event_send(1, [])

    def load(self, txt):
        data = open(txt, 'r').read()
        code = scripting.grammar.parse(data)
        self.evaluator.eval_code(code)