from super_vertex import SuperVertex

class SmartEdge(object):
    def __init__(self):
        self.min_edge = float("inf")
        self.max_edge = float("-inf")

    def add(self, weight):
        self.min_edge = min(self.min_edge, weight)
        self.max_edge = max(self.max_edge, weight)

class EdgeMap(object):
    def __init__(self):
        self.edges = {}

    def merge(self, edge_map, source_key, new_key):
        pass         

    def connect(self, v1, v2, weight):
        if v1 not in self.edges:
            self.edges[v1] = {}

        if v2 not in self.edges[v1]:
            self.edges[v1][v2] = SmartEdge()

        self.edges[v1][v2].add(weight)

    def drop_vertex(self, v):
        del self.edges[v]

    def drop(self, v1, v2):
        del self.edges[v1][v2]

    def __getitem__(self, pos_arg):
        return self.edges.__getitem__(pos_arg)

    def __iter__(self):
        return self.edges.__iter__()

    def values(self):
        return self.edges.values()

class Graph(object):
    def __init__(self, vertices_map):
        self.vertices = {}
        self.sv_map = {}
        self.edges = EdgeMap()

        for v in vertices_map:
            sv = SuperVertex()
            sv.add(vertices_map[v])
            self.sv_map[v] = sv.identity
            self.vertices[sv.identity] = sv

        self.sorted_edges = self.__sorted_edges(vertices_map)

        for (v1, v2, weight) in self.sorted_edges:
            self.edges.connect(self.sv_map[v1], self.sv_map[v2], weight)
            self.edges.connect(self.sv_map[v2], self.sv_map[v1], weight)

        self.max_edge = self.sorted_edges[-1][2]
        self.singular_vertices_no = len(vertices_map)
        self.within_cluster_distance = 0.
        self.cluster_edginess = sum(map(len, self.edges.values()))
        self.between_cluster_distance = 2. * sum(map(lambda x: x[2], 
                                                 self.sorted_edges))

    def __sorted_edges(self, vertices_map):
        s = set()

        for key in vertices_map:
            for similar in vertices_map[key]['similars']:
                track = vertices_map[key]
                s.add((min(track['track_id'], similar[0]),
                       max(track['track_id'], similar[0]),
                       1 / similar[1]))

        return sorted(s, key=lambda x: x[2])

    def has_vertex(self, vertex_id):
        return vertex_id in self.sv_map

    def loss(self):
        a = self.within_cluster_distance
        b = self.max_edge * self.singular_vertices_no
        c = self.cluster_edginess
        d = self.between_cluster_distance
        return (a + b) * c / d, a, b, c, d

    def loss_change(self, sv1_id, sv2_id, merged_edges):
        sv1_max_edge = self.vertices[sv1_id].max_edge
        sv2_max_edge = self.vertices[sv2_id].max_edge
        new_max_edge = max([sv1_max_edge, sv2_max_edge, self.edges[sv1_id][sv2_id].max_edge])
        sv1_size = self.vertices[sv1_id].count()
        sv2_size = self.vertices[sv2_id].count()
        total_size = sv1_size + sv2_size

        a_diff = total_size * new_max_edge
        a_diff -= sv1_size * sv1_max_edge
        a_diff -= sv2_size * sv2_max_edge
        size_one_svs = 0
        if self.vertices[sv1_id].count() == 1:
            size_one_svs -= 1
        if self.vertices[sv2_id].count() == 1:
            size_one_svs -= 1
        b_diff = self.max_edge * size_one_svs

        merged_edges = self.merge_edges(sv1_id, sv2_id)
        c_diff = total_size * len(merged_edges[sv1_id, sv2_id]) 
        c_diff -= sv1_size * len(self.edges[sv1_id])
        c_diff -= sv2_size * len(self.edges[sv2_id])
        doubled = list(set(self.edges[sv1_id].keys()) & set(self.edges[sv2_id].keys()))
        for v in doubled:
            c_diff -= len(self.edges[v]) - 1


        d_diff = 0.
        for v in merged_edges[sv1_id, sv2_id]:
            d_diff += (total_size + self.vertices[v].count()) * merged_edges[sv1_id, sv2_id][v].min_edge
        for v in self.edges[sv1_id]:
            d_diff -= (sv1_size + self.vertices[v].count()) * self.edges[sv1_id][v].min_edge
        for v in self.edges[sv2_id]:
            d_diff -= (sv2_size + self.vertices[v].count()) * self.edges[sv2_id][v].min_edge
        try:
            d_diff -= total_size * self.edges[sv1_id][sv2_id].min_edge
        except KeyError:
            pass
        loss, a, b, c, d = self.loss()

        an = a + a_diff
        bn = b + b_diff
        cn = c + c_diff
        dn = d + d_diff

        return (an + bn) * cn / dn, loss, (an, bn, cn, dn)

    def merge_edges(self, sv1_id, sv2_id):
        edges = EdgeMap()
        for v in self.edges[sv1_id]:
            if v != sv2_id:
                edges.connect((sv1_id, sv2_id), v, self.edges[sv1_id][v].min_edge)
                edges.connect((sv1_id, sv2_id), v, self.edges[sv1_id][v].max_edge)

        for v in self.edges[sv2_id]:
            if v != sv1_id:
                edges.connect((sv1_id, sv2_id), v, self.edges[sv2_id][v].min_edge)
                edges.connect((sv1_id, sv2_id), v, self.edges[sv2_id][v].max_edge)

        return edges

    def reduce(self):
        improvable = True
        while improvable:
            improvable = False
            for (i, (v1, v2, _)) in enumerate(self.sorted_edges):
                sv1_id = self.sv_map[v1]
                sv2_id = self.sv_map[v2]
                merged_edges = self.merge_edges(sv1_id, sv2_id)
                new_loss, old_loss, (a, b, c, d) = self.loss_change(sv1_id, sv2_id, merged_edges)
                if new_loss < old_loss:
                    self.within_cluster_distance = a
                    self.singular_vertices_no = b / self.max_edge
                    self.cluster_edginess = c
                    self.between_cluster_distance = d

                    new_sv = SuperVertex()
                    for k in self.vertices[sv1_id].map:
                        new_sv.add(self.vertices[sv1_id].map[k])
                    for k in self.vertices[sv2_id].map:
                        new_sv.add(self.vertices[sv2_id].map[k])
                    new_id = new_sv.identity
                    self.vertices[new_id] = new_sv
                    for v in new_sv.map:
                        self.sv_map[v] = new_id
                    print self.sv_map
                    self.edges.merge(merged_edges, (sv1_id, sv2_id), new_id)
                    for v in merged_edges[sv1_id, sv2_id]:
                        self.edges.connect(v, new_id, merged_edges[sv1_id, sv2_id][v])
                    self.edges.drop_vertex(sv1_id)
                    self.edges.drop_vertex(sv2_id)

                    del(self.vertices[sv1_id])
                    del(self.vertices[sv2_id])
                    
                    improvable = True
                    break

