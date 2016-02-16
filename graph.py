import numpy as np

class SmartEdge(object):
    def __init__(self):
        self.min_edge = float("inf")
        self.max_edge = float("-inf")

    def add(self, weight):
        self.min_edge = min(self.min_edge, weight)
        self.max_edge = max(self.max_edge, weight)

    def __repr__(self):
        return "(%.2f, %.2f)" % (self.min_edge, self.max_edge)

class EdgeMap(object):
    def __init__(self):
        self.edges = {}

    def merge(self, edge_map, source_key, new_key):
        for v in edge_map[source_key]:
            self.connect(new_key, v, edge_map[source_key][v].min_edge)
            self.connect(new_key, v, edge_map[source_key][v].max_edge)

    def connect(self, v1, v2, weight):
        if v1 not in self.edges:
            self.edges[v1] = {}

        if v2 not in self.edges[v1]:
            self.edges[v1][v2] = SmartEdge()

        self.edges[v1][v2].add(weight)

    def min_edges_list(self):
        return [(v1, v2, self.edges[v1][v2].min_edge) for v1 in self.edges for v2 in self.edges[v1]]

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

    def debug(self):
        #print self.edges
        pass

class Graph(object):
    def __init__(self, vertices_map):
        self.vertices = {}
        self.sv_map = {}
        self.edges = EdgeMap()
        empties = 0
        for v in vertices_map:
            sv = SuperVertex()
            sv.add(vertices_map[v])
            self.sv_map[v] = sv.identity
            self.vertices[sv.identity] = sv
            if len(vertices_map[v]['similars']) == 0:
                empties += 1

        self.sorted_edges = self.__sorted_edges(vertices_map)

        for (v1, v2, weight) in self.sorted_edges:
            if v1 in vertices_map and v2 in vertices_map:
                self.edges.connect(self.sv_map[v1], self.sv_map[v2], weight)
                self.edges.connect(self.sv_map[v2], self.sv_map[v1], weight)

        if len(self.sorted_edges) != 0:
            self.max_edge = self.sorted_edges[-1][2]
        else:
            self.max_edge = 0.
        self.singular_vertices_no = len(vertices_map)
        self.within_cluster_distance = 0.
        self.between_cluster_distance = sum(map(lambda x: x[2],
                                                self.sorted_edges))


    def __sorted_edges(self, vertices_map):
        s = set()

        for key in vertices_map:
            for similar in vertices_map[key]['similars']:
                track = vertices_map[key]
                first_v = track['track_id']
                second_v = similar
                similarity = vertices_map[key]['similars'][second_v]
                if first_v in self.sv_map and second_v in self.sv_map:
                    s.add((min(first_v, second_v),
                           max(first_v, second_v),
                           1 / similarity))

        return sorted(s, key=lambda x: x[2])

    def has_vertex(self, vertex_id):
        return vertex_id in self.sv_map

    def loss(self):
        a = self.within_cluster_distance
        b = self.max_edge * self.singular_vertices_no
        d = self.between_cluster_distance
        return (a + 2 * b) * d, a, b, d

    def loss_change(self, sv1_id, sv2_id, merged_edges):
        sv1_max_edge = self.vertices[sv1_id].max_edge
        sv2_max_edge = self.vertices[sv2_id].max_edge
        new_max_edge = max([sv1_max_edge, sv2_max_edge, self.edges[sv1_id][sv2_id].max_edge])
        sv1_size = self.vertices[sv1_id].count()
        sv2_size = self.vertices[sv2_id].count()
        total_size = sv1_size + sv2_size

        a_diff = new_max_edge
        a_diff -= sv1_max_edge
        a_diff -= sv2_max_edge
        size_one_svs = 0
        if self.vertices[sv1_id].count() == 1:
            size_one_svs -= 1
        if self.vertices[sv2_id].count() == 1:
            size_one_svs -= 1
        b_diff = self.max_edge * size_one_svs

        merged_edges = self.merge_edges(sv1_id, sv2_id)

        d_diff = 0.

        if (sv1_id, sv2_id) in merged_edges:
            for v in self.edges[sv1_id]:
                d_diff -= self.edges[sv1_id][v].min_edge
            for v in self.edges[sv2_id]:
                d_diff -= self.edges[sv2_id][v].min_edge
            for v in merged_edges[sv1_id, sv2_id]:
                d_diff += merged_edges[sv1_id, sv2_id][v].min_edge
            d_diff += self.edges[sv1_id][sv2_id].min_edge
        else:
            d_diff = self.edges[sv1_id][sv2_id].min_edge
        loss, a, b, d = self.loss()

        an = a + a_diff
        bn = b + b_diff
        dn = d + d_diff

        return (an + 2 * bn) * dn, loss, (an, bn, dn)

    def merge_edges(self, sv1_id, sv2_id):
        edges = EdgeMap()
        if sv1_id in self.edges:
            for v in self.edges[sv1_id]:
                if v != sv2_id:
                    edges.connect((sv1_id, sv2_id), v, self.edges[sv1_id][v].min_edge)
                    edges.connect((sv1_id, sv2_id), v, self.edges[sv1_id][v].max_edge)

        if sv2_id in self.edges:
            for v in self.edges[sv2_id]:
                if v != sv1_id:
                    edges.connect((sv1_id, sv2_id), v, self.edges[sv2_id][v].min_edge)
                    edges.connect((sv1_id, sv2_id), v, self.edges[sv2_id][v].max_edge)

        return edges

    def distance_matrix(self):
        matrix = np.ndarray(shape=(len(self.vertices), len(self.vertices)), dtype=float)
        matrix.fill(float("inf"))
        np.fill_diagonal(matrix, 0)

        next_id = 0
        vertices_numbering = {}
        for i in self.vertices:
           vertices_numbering[i] = next_id
           next_id += 1

        for (v1, v2, cost) in self.edges.min_edges_list():
            v1pos = vertices_numbering[v1]
            v2pos = vertices_numbering[v2]
            matrix[v1pos, v2pos] = cost

        for u in self.vertices:
            for v1 in self.vertices:
                for v2 in self.vertices:
                    upos = vertices_numbering[u]
                    v1pos = vertices_numbering[v1]
                    v2pos = vertices_numbering[v2]

                    through_u = matrix[v1pos, u] + matrix[u, v2pos]
                    matrix[v1pos, v2pos] = min(through_u, matrix[v1pos, v2pos])

        return matrix, vertices_numbering

    def reduce(self, min_elems=50):
        improvable = True
        iterations = 0
        while improvable and len(self.vertices) > min_elems:
            #print "* Iteration %d" % (iterations)
            #print "* Vertices: %d" % len(self.vertices)

            improvable = False
            if len(self.vertices) > 1:
                position_to_pop = None
                for (i, (v1, v2, _)) in enumerate(self.sorted_edges):
                    if len(self.vertices) < 10:
                        #print self.sv_map
                        #print self.vertices
                        self.edges.debug()
                        #print self.sorted_edges
                    sv1_id = self.sv_map[v1]
                    sv2_id = self.sv_map[v2]
                    merged_edges = self.merge_edges(sv1_id, sv2_id)

                    if sv1_id == sv2_id:
                        continue

                    new_loss, old_loss, (a, b, d) = self.loss_change(sv1_id, sv2_id, merged_edges)
                    if new_loss < old_loss:
                        # print "* Merging. Old loss: %.5f. New loss: %.5f; NTH element: %d" % (old_loss,  new_loss, i)
                        # print a, b, d
                        self.within_cluster_distance = a
                        self.singular_vertices_no = b / self.max_edge
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
                        if (sv1_id, sv2_id) in merged_edges:
                            self.edges.merge(merged_edges, (sv1_id, sv2_id), new_id)
                            for v in merged_edges[sv1_id, sv2_id]:
                                self.edges.connect(v, new_id, merged_edges[sv1_id, sv2_id][v].min_edge)
                                self.edges.connect(v, new_id, merged_edges[sv1_id, sv2_id][v].max_edge)

                        for v in self.edges[sv1_id]:
                            self.edges.drop(v, sv1_id)
                        for v in self.edges[sv2_id]:
                            self.edges.drop(v, sv2_id)

                        self.edges.drop_vertex(sv1_id)
                        self.edges.drop_vertex(sv2_id)

                        del(self.vertices[sv1_id])
                        del(self.vertices[sv2_id])

                        improvable = True
                        iterations += 1
                        position_to_pop = i
                        break
                    # else:
                        # print "* WRONG. Old loss: %.5f. New loss: %.5f; NTH element: %d" % (old_loss,  new_loss, i)
                        # print a, b, d
                if position_to_pop is not None:
                    #self.sorted_edges.pop(position_to_pop)
                    self.sorted_edges = self.sorted_edges[position_to_pop+1:]
                    #self.sorted_edges = self.sorted_edges[position_to_pop+1:] + self.sorted_edges[:position_to_pop]
        print len(self.vertices)
        for v in self.vertices:
            if len(self.vertices[v].map) < min_elems:
                self.vertices[v] = self.vertices[v].build_flat()
            else:
                self.vertices[v] = self.vertices[v].build()
            self.vertices[v].reduce(min_elems=min_elems)

class FlatGraph(Graph):
    def reduce(self, min_elems=50):
        #print "* Flat graph reduce is no-op."
        pass

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
        for v in vertex['similars']:
            if v in self.map:
                self.max_edge = max(self.max_edge, vertex['similars'][v])

    def count(self):
        return len(self.map.keys())

    def build(self):
        return Graph(self.map)

    def build_flat(self):
        return FlatGraph(self.map)
