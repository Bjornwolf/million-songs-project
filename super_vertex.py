from graph import Graph

class SuperVertex(object):
    NEXT_SV_ID = 0

    def __init__(self, vertex):
       first_vertex_map = dict()
       self.__internal = Graph()

    def internal_vertices_count(self):

    def __getitem__(self, key, val):
        if key in ['tags', 'similars']:
            return { 'tags': self.tags,
                     'similars': self.similars_from_edges() 
                   }[key]
        else
            raise KeyError
