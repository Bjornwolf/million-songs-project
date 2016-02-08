from graph import Graph

class SuperVertex(object):
    def __init__(self):
        self.__graph = None
        self.__map = dict()

    def add(self, vertex):
        self.__map[vertex['track_id']] = vertex

    def build(self):
        return Graph(self.__map)
