class SuperVertex(object):
    ID = 0
    def __init__(self):
        self.__graph = None
        self.map = dict()
        self.identity = SuperVertex.ID
        self.max_edge = 0.
        SuperVertex.ID += 1

    def add(self, vertex):
        self.map[vertex['track_id']] = vertex
        for v, w in vertex['similars']:
            if v in self.map:
                self.max_edge = max(self.max_edge, w)

    def count(self):
        return len(self.map.keys())

    def build(self):
        return Graph(self.map)
