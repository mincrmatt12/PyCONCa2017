import font


class PriceLabels:
    def __init__(self, geom, tag):
        self.geoms = geom.geoms
        self.label_data = {}
        self.load(tag)

    def find_geom_by_ref(self, ref):
        for geom in self.geoms:
            if geom.ref == ref:
                return geom
        return None

    def geom_center_by_ref(self, ref):
        geom = self.find_geom_by_ref(ref)
        return geom.aabb

    def load(self, tag):
        for item in tag['prices']:
            if len(tag['prices'][item]) == 2:
                price, name = tag['prices'][item]
                self.label_data[self.find_geom_by_ref(item)] = ["  {}\n${:,.2f}".format(name, price),
                                                                self.geom_center_by_ref(item)]
            else:
                name = tag['prices'][item][0]
                self.label_data[self.find_geom_by_ref(item)] = ["{}".format(name), self.geom_center_by_ref(item)]