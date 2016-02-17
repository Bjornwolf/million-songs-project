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

#class EdgeMap(object):
#    def __init__(self):
#        self.edges = {}
#
#    def merge(self, edge_map, source_key, new_key):
#        for v in edge_map[source_key]:
#            self.connect(new_key, v, edge_map[source_key][v].min_edge)
#            self.connect(new_key, v, edge_map[source_key][v].max_edge)
#
#    def connect(self, v1, v2, weight):
#        if v1 not in self.edges:
#            self.edges[v1] = {}
#
#        if v2 not in self.edges[v1]:
#            self.edges[v1][v2] = SmartEdge()

#        self.edges[v1][v2].add(weight)

#    def min_edges_list(self):
#        return [(v1, v2, self.edges[v1][v2].min_edge) for v1 in self.edges for v2 in self.edges[v1]]

#    def drop_vertex(self, v):
#        del self.edges[v]

#    def drop(self, v1, v2):
#        del self.edges[v1][v2]

#    def __getitem__(self, pos_arg):
#        return self.edges.__getitem__(pos_arg)

#    def __iter__(self):
#        return self.edges.__iter__()

#    def values(self):
#        return self.edges.values()

class EdgeMap(object):
    def __init__(self):
        self.edges = SortedDict

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
            improvable = False
            if len(self.vertices) > 1:
                position_to_pop = None
                for (i, (v1, v2, _)) in enumerate(self.sorted_edges):
                    if len(self.vertices) < 10:
                        self.edges.debug()
                    sv1_id = self.sv_map[v1]
                    sv2_id = self.sv_map[v2]
                    merged_edges = self.merge_edges(sv1_id, sv2_id)

                    if sv1_id == sv2_id:
                        continue

                    new_loss, old_loss, (a, b, d) = self.loss_change(sv1_id, sv2_id, merged_edges)
                    if new_loss < old_loss:
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
                if position_to_pop is not None:
                    self.sorted_edges = self.sorted_edges[position_to_pop+1:]
        print len(self.vertices)
        for v in self.vertices:
            if len(self.vertices[v].map) < min_elems:
                self.vertices[v] = self.vertices[v].build_flat()
            else:
                self.vertices[v] = self.vertices[v].build()
            self.vertices[v].reduce(min_elems=min_elems)

class FlatGraph(Graph):
    def reduce(self, min_elems=50):
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

from Banyan import SortedSet

class SingleVertexGraph(object):
    def __init__(self, vertex_id):
        self.id = vertex_id
        self.is_single = True
        self.edges = {}
        self.subgraphs = {}
        self.subgraphs_order = SortedSet(key=lambda x: x.count())

    def loss(self):
        pass

    def loss_change(self, vertex_id, neighbour_id):
        pass

    def reduce(self, min_elems=100):
        pass

    def count(self):
        return 1

class NewGraph(object):
    ID = 0

    def __init__(self, vertices_map):
        self.is_single = False
        self.wrap_with_subgraphs(vertices_map)
        self.establish_subgraphs_order()
        self.build_loss_parameters()

        self.id = NewGraph.ID
        NewGraph.ID += 1
    
    def count(self):
        return len(self.subgraphs)

    def establish_subgraphs_order(self):
        self.subgraphs_order = SortedSet(self.subgraphs.keys(), 
                                         key=lambda x: x.count())

    def wrap_with_subgraphs(self, vertices_map):
        self.subgraphs = {}
        self.known_ids = set(vertices_map.keys())
        self.edges = {}
        for vertex_id in vertices_map:
            self.edges[vertex_id] = {}
            for key in vertices_map[vertex_id]['similars']:
                weight = vertices_map[vertex_id]['similars'][key]
                self.edges[vertex_id][key] = [(vertex_id, key, weight)]
            del(vertices_map[vertex_id]['similars'])
            new_subgraph = SingleVertexGraph(vertex_id)
            self.subgraphs[new_subgraph.id] = new_subgraph

    def build_loss_parameters(self):
        self.within_cluster_distance = 0.
        self.singular_vertices_no = len(self.subgraphs)
        self.between_cluster_distance = 0.
        self.max_weight = 0.
        for from_v in self.edges:
            for to_w in self.edges[from_v]:
                edge_list = self.edges[from_v][to_w]
                edge_weights = map(lambda x: x[2], edge_list)
                self.max_weight = max(max(edge_weights), self.max_weight)
                self.between_cluster_distance +=sum(edge_weights)
        self.between_cluster_distance /= 2.

    def loss(self):
        wcd = self.within_cluster_distance
        svp = self.max_weight * self.singular_vertices_no
        bcd = self.between_cluster_distance
        # pomysl loss * self.vertices[self.vertices_order[-1]].count()
        return (wcd + svp) * bcd

    def reduce(self, min_elems=100):
        improvable = True
        while improvable and self.count() > min_elems:
            improvable = False
            improvement_point = None
            loss = self.loss()

            for subgraph_id in self.subgraphs_order:
                subgraph = self.subgraphs[subgraph_id]
                for neighbour_id in self.edges[subgraph_id]: 
                    new_loss = self.loss_after_merge(subgraph_id, neighbour_id)

                    if new_loss < loss:
                        new_subgraph_id = self.merge_subgraphs(subgraph_id, neighbour_id)
                        improvement_point = (subgraph_id, neighbour_id, new_sv_id)
                        break
                if improvement_point:
                    improvable = True
                    break
            self.cleanup_subgraphs(improvement_point)
        print "Reducing subgraphs..."
        for subgraph_id in self.subgraphs:
            self.subgraphs[subgraph_id].reduce(min_elems=min_elems)
        print "Reduction complete!"

    def loss_after_merge(self, subgraph_id, neighbour_id):
        weight = self.edges[subgraph_id][neighbour_id][-1][2]
        max_e = lambda v: self.subgraphs[v].max_weight
        plus_candidate = max(max_e(subgraph_id), max_e(neighbour_id))
        plus_candidate = max(plus_candidate, weight)
        delta_wcd = plus_candidate - max_e(subgraph_id) - max_e(neighbour_id)

        delta_svp = 0
        if self.subgraphs[subgraph_id].is_single:
            delta_svp -= 1
        if self.subgraphs[neighbour_id].is_single:
            delta_svp -= 1

        
        edge_weight = lambda edges: edges[0][2]
        min_weight_sum = lambda v: sum([edge_weight(self.edges[v][w]) for w in self.edges[v]])
        delta_bcd = weight - min_weight_sum(subgraph_id) - min_weight_sum(neighbour_id)
        new_edges = self.adjacent_edges(subgraph_id, neighbour_id)
        delta_bcd += sum(new_edges.values())

        new_wcd = self.within_cluster_distance + delta_wcd
        new_svp = (self.singular_vertices_no + delta_svp) * self.max_weight
        new_bcd = self.between_cluster_distance + delta_bcd
        return (new_wcd + new_svp) * new_bcd

    def adjacent_edges(self, subgraph_id, neighbour_id):
        adjacent_edges = {k: self.edges[subgraph_id][0][2] for k in
                self.edges[subgraph_id]}
        neighbour_similars = self.edges[neighbour_id]
        for neighbour_adjacent in neighbour_similars:
            current_edge_weight = neighbour_similars[neighbour_adjacent][0][2]
            if neighbour_adjacent in adjacent_edges:
                existing_edge_weight = adjacent_edges[neighbour_adjacent]
                adjacent_edges[neighbour_adjacent] = min(existing_edge_weight, 
                                                         current_edge_weight)
            else:
                adjacent_edges[neighbour_adjacent] = current_edge_weight 
        return adjacent_edges

    def extract_edges(self, subgraph_id, neighbour_id):
        edges_between = self.edges[subgraph_id][neighbour_id]
        edges_between_dict = {}
        for (u, v, w) in edges_between:
            if u not in edges_between_dict:
                edges_between_dict[u] = {}
            if v not in edges_between_dict[u]:
                edges_between_dict[u][v] = []
            edges_between_dict[u][v].append( (u, v, w) )
        return edges_between_dict

    def merge_edges(self, subgraph_id, neighbour_id):
        edges_from_left = self.subgraphs[subgraph_id].edges
        edges_from_right = self.subgraphs[neighbour_id].edges
        edges_left_to_right = self.extract_edges(subgraph_id, neighbour_id)
        edges_right_to_left = self.extract_edges(neighbour_id, subgraph_id)

        new_graph_edges = edges_left_to_right
        for v1 in edges_right_to_left:
            if v1 not in new_graph_edges:
                new_graph_edges[v1] = {}
            for v2 in edges_right_to_left[v1]:
                new_graph_edges[v1][v2] = edges_right_to_left[v1][v2]

        for v1 in edges_from_left:
            if v1 not in new_graph_edges:
                new_graph_edges[v1] = {}
            for v2 in edges_from_left[v1]:
                if v2 not in new_graph_edges[v1]:
                    new_graph_edges[v1][v2] = []
                new_graph_edges[v1][v2] += edges_from_left[v1][v2]

        for v1 in edges_from_right:
            if v1 not in new_graph_edges:
                new_graph_edges[v1] = {}
            for v2 in edges_from_right[v1]:
                if v2 not in new_graph_edges[v1]:
                    new_graph_edges[v1][v2] = []
                new_graph_edges[v1][v2] += edges_from_right[v1][v2]

        new_subgraphs = self.subgraphs[subgraph_id].subgraphs
        for right_subgraph_id in self.subgraphs[neighbour_id].subgraphs:
            new_subgraphs[right_subgraph_id] = self.subgraphs[neighbour_id].subgraphs[right_subgraph_id]

        new_subgraphs_order = self.subgraphs[subgraph_id].subgraphs_order |
        self.subgraphs[neighbour_id].subgraphs_order

        new_graph = NewGraph(subgraphs=new_subgraphs,
                          subgraphs_order=new_subgraphs_order, 
                          edges=new_graph_edges)

        del(self.edges[subgraph_id][neighbour_id])
        del(self.edges[neighbour_id][subgraph_id])
        self.edges[new_graph.id] = {}
        for v2 in self.edges[subgraph_id]:
            self.edges[new_graph.id][v2] = self.edges[subgraph_id][v2]
            self.edges[v2][new_graph.id] = self.edges[v2][subgraph_id]
        for v2 in self.edges[neighbour_id]:
            if v2 not in self.edges[new_graph.id]:
                self.edges[new_graph.id][v2] = []
            self.edges[new_graph.id][v2] = self.merge_sorted_lists(
                    self.edges[neighbour_id][v2],
                    self.edges[new_graph.id][v2])
            
            if new_graph.id not in self.edges[v2]:
                self.edges[v2][new_graph.id] = []
            self.edges[v2][new_graph.id] = self.merge_sorted_lists(
                    self.edges[v2][new_graph.id]
                    self.edges[v2][neighbour_id])

        self.subgraphs[new_graph.id] = new_graph
        return new_graph.id

    def merge_sorted_lists(self, l1, l2):
        result = []
        i = 0
        j = 0
        while i < len(l1) and j < len(l2):
            if l1[i][2] < l2[j][2]:
                result.append(l1[i])
                i += 1
            else:
                result.append(l2[j])
                j += 1
        return result + l1[i:] + l2[j:]

        # TODO zrobic nowy graf, wjebac wierzcholki, wjebac krawedzie
        # TODO poprawic polaczenia miedzy reszta grafu a nowym grafem
        
