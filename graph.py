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

        self.sorted_edges = self.__sorted_edges(vertices_map) 

        for (v1, v2, weight) in self.sorted_edges:
            try:
                self.edges[self.sv_map[v1]][self.sv_map[v2]] = weight
            except KeyError:
                self.edges[self.sv_map[v1]] = {}
                self.edges[self.sv_map[v1]][self.sv_map[v2]] = weight
            try:
                self.edges[self.sv_map[v2]][self.sv_map[v1]] = weight
            except KeyError:
                self.edges[self.sv_map[v2]] = {}
                self.edges[self.sv_map[v2]][self.sv_map[v1]] = weight

        self.max_edge = self.sorted_edges[-1][2]
        self.singular_vertices_no = len(vertices_map)
        self.within_cluster_distance = 0.
        self.cluster_edginess = sum(self.edges.values())
        self.between_cluster_distance = sum(map(lambda x: x[2], 
                                            self.sorted_edges))

    def __sorted_edges(self, vertices_map):
        s = set()

        for key in vertices_map:
            for similar in vertices_map[key]['similars']:
                track = vertices_map[key]
                s.add((min(track['trackid'], similar[0]), 
                       max(track['trackid'], similar[0]),
                       1 / similar[1]))

        return sorted(s, lambda x: x[2])

    def has_vertex(vertex_id):
        return vertex_id in self.sv_map

    def loss(self):
        a = self.within_cluster_distance
        b = self.max_edge * self.singular_vertices
        c = self.cluster_edginess
        d = self.between_cluster_distance
        return (a + b) * c / d

    def loss_change(self, sv1_id, sv2_id, merged_edges=None):
        sv1_max_edge = max(self.edges[sv1_id].values())
        sv2_max_edge = max(self.edges[sv2_id].values())
        new_max_edge = max(sv1_max_edge, sv2_max_edge)
        sv1_size = self.vertices[sv1_id].size()
        sv2_size = self.vertices[sv2_id].size()
        total_size = sv1_size + sv2_size

        a_diff = total_size * new_max_edge
        a_diff -= sv1_size * sv1_max_edge
        a_diff -= sv2_size * sv2_max_edge
        size_one_svs = 0
        if self.vertices[sv1_id].size() == 1:
            size_one_svs += 1
        if self.vertices[sv2_id].size() == 1:
            size_one_svs += 1
        b_diff = self.max_edge * size_one_svs

        if not merged_edges: 
            merged_edges = self.merge_edges(sv1_id, sv2_id)
        c_diff = total_size * len(merged_edges) 
        c_diff -= sv1_size * len(self.edges[sv1_id])
        c_diff -= sv2_size * len(self.edges[sv2_id])

        d_diff = 0.
        for v in merged_edges:
            d_diff += (total_size + self.vertices[v].size()) * merged_edges[v]
        for v in self.edges[sv1_id]:
            d_diff -= (sv1_size + self.vertices[v].size()) * self.edges[sv1_id][v]
        for v in self.edges[sv2_id]:
            d_diff -= (sv2_size + self.vertices[v].size()) * self.edges[sv2_id][v]
        try:
            d_diff -= total_size * self.edges[sv1_id][sv2_id]
        except KeyError:
            pass

        an = a + a_diff
        bn = b + b_diff
        cn = c + c_diff
        dn = d + d_diff

        return (an + bn) * cn / dn - self.loss()

    def merge_edges(self, sv1_id, sv2_id):
        edges = {}
        for v in self.edges[sv1_id]:
            if v != sv2_id:
                edges[v] = self.edges[sv1_id][v]
        for v in self.edges[sv2_id]:
            if v != sv1_id:
                if v in edges:
                    edges[v] = min(edges[v], self.edges[sv2_id][v])
                else:
                    edges[v] = self.edges[sv2_id][v]
        return edges

    def reduce(self):
        pass

