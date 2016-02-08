class Graph(object):
    def __init__(self, vertices_map):
        self.vertices = {}
        self.sv_map = {}
        self.edges = {}

        for v in vertices_map:
            sv = SuperVertex()
            sv.add(vertices_map[v])
            self.sv_map[v] = sv.identity
            self.vertices[sv.identity] = sv

        self.sorted_edges = get_sorted_edges(vertices_map) #TODO
        for (v1, v2, weight) in self.sorted_edges:
            try:
                self.edges[self.sv_map[v1]].append((self.sv_map[v2], weight))
            except KeyError:
                self.edges[self.sv_map[v1]] = [(self.sv_map[v2], weight)]

        self.max_edge = self.sorted_edges[-1][2]
        self.singular_vertices_no = len(vertices_map)
        self.within_cluster_distance = 0.
        self.cluster_edginess = sum(self.edges.values())
        self.between_cluster_distance = sum(map(lambda x: x[2], 
                                            self.sorted_edges))

    def has_vertex(vertex_id):
        return vertex_id in self.sv_map

    def loss(self):
        a = self.within_cluster_distance
        b = self.max_edge * self.singular_vertices
        c = self.cluster_edginess
        d = self.between_cluster_distance
        return (a + b) * c / d

    def loss_change(self, vertex_id):
        pass

    def reduce(self):
        pass

class Graph(object):
    def __init__(self, vertices):
        self.sorted_edges = self._build_edge_list(vertices.values())

        self.max_edge = self.sorted_edges[-1][2] 

        self.within_cluster_distance = 0.
        self.cluster_edginess = 
        self.between_cluster_distance = 

    def size(self):
        return len(self.vertices)

    def _build_edges_list(self, train_data):
        edges = set()
