import numpy as np
import cPickle as pickle
from banyan import SortedSet

class SingleVertexGraph(object):
    def __init__(self, vertex_id):
        def compare(x, y):
            if self.subgraphs[x].count() == self.subgraphs[y].count():
                if x < y:
                    return -1
                elif x > y:
                    return 1
                else:
                    return 0
            elif self.subgraphs[x].count() < self.subgraphs[y].count():
                return -1
            else:
                return 1
        self.id = vertex_id
        self.is_single = True
        self.edges = {}
        self.subgraphs = {vertex_id: self}
        self.max_weight = 0.
        self.subgraphs_order = SortedSet(compare=compare)
        self.subgraphs_order.add(vertex_id)

    def distance_matrix(self):
        self.distance_matrix = np.zeros((1, 1))

    def loss(self):
        pass

    def loss_change(self, vertex_id, neighbour_id):
        pass

    def reduce(self, min_elems=100):
        pass

    def simplify_edges(self):
        pass

    def count(self):
        return 1

    def pickle_graph(self, path):
        with open(path + 'graph' + str(self.id) + '.p', 'wb') as f:
            pickle.dump( (self.distance_matrix, self.subgraphs.keys()), f)


class NewGraph(object):
    ID = -1

    def __init__(self, vertices_map=None, edges=None, subgraphs=None, subgraphs_order=None):
        if vertices_map is None:
            self.subgraphs = subgraphs
            self.edges = edges
            self.subgraphs_order = subgraphs_order
        else:
            self.wrap_with_subgraphs(vertices_map)
            self.establish_subgraphs_order()
        self.is_single = False
        self.build_loss_parameters()

        self.id = NewGraph.ID
        NewGraph.ID -= 1
        self.merged = []
    
    def count(self):
        return len(self.subgraphs)

    def establish_subgraphs_order(self):
        def compare(x, y):
            if self.subgraphs[x].count() == self.subgraphs[y].count():
                if x < y:
                    return -1
                elif x > y:
                    return 1
                else:
                    return 0
            elif self.subgraphs[x].count() < self.subgraphs[y].count():
                return -1
            else:
                return 1

        self.subgraphs_order = SortedSet(self.subgraphs.keys(), compare=compare)

    def wrap_with_subgraphs(self, vertices_map):
        self.subgraphs = {}
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
                        improvement_point = (subgraph_id, neighbour_id, new_subgraph_id)
                        break
                if improvement_point:
                    improvable = True
                    break
        print "Reducing subgraphs..."
        for subgraph_id in self.subgraphs:
            self.subgraphs[subgraph_id].reduce(min_elems=min_elems)
        print "Reduction complete!"
        self.simplify_edges()
        print "Simplified edges..."

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
        adjacent_edges = {k: self.edges[subgraph_id][k][0][2] for k in
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

    def simplify_edges(self):
        for v1 in self.edges:
            for v2 in self.edges[v1]:
                self.edges[v1][v2] = self.edges[v1][v2][0][2]

    def merge_subgraphs(self, subgraph_id, neighbour_id):
        def compare(x, y):
            if new_subgraphs[x].count() == new_subgraphs[y].count():
                if x < y:
                    return -1
                elif x > y:
                    return 1
                else:
                    return 0
            elif new_subgraphs[x].count() < new_subgraphs[y].count():
                return -1
            else:
                return 1
        edges_from_left = self.subgraphs[subgraph_id].edges
        edges_from_right = self.subgraphs[neighbour_id].edges
        edges_left_to_right = self.extract_edges(subgraph_id, neighbour_id)
        edges_right_to_left = self.extract_edges(neighbour_id, subgraph_id)
 
        new_graph_edges = {}
        for v1 in edges_left_to_right:
            if v1 not in new_graph_edges:
                new_graph_edges[v1] = {}
            for v2 in edges_left_to_right[v1]:
                new_graph_edges[v1][v2] = edges_left_to_right[v1][v2]

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
        new_subgraphs = {}
        for sg in self.subgraphs[subgraph_id].subgraphs:
            new_subgraphs[sg] = self.subgraphs[subgraph_id].subgraphs[sg]
        for right_subgraph_id in self.subgraphs[neighbour_id].subgraphs:
            new_subgraphs[right_subgraph_id] = self.subgraphs[neighbour_id].subgraphs[right_subgraph_id]

        new_subgraphs_order = list(self.subgraphs[subgraph_id].subgraphs_order)
        new_subgraphs_order += list(self.subgraphs[neighbour_id].subgraphs_order)
        new_subgraphs_order = SortedSet(new_subgraphs_order, compare=compare)
        self.subgraphs_order.remove(subgraph_id)
        self.subgraphs_order.remove(neighbour_id)
        new_graph = NewGraph(subgraphs=new_subgraphs,
                          subgraphs_order=new_subgraphs_order, 
                          edges=new_graph_edges,
                          vertices_map=None)
       
        del(self.edges[subgraph_id][neighbour_id])
        del(self.edges[neighbour_id][subgraph_id])
        
        self.edges[new_graph.id] = {}
        all_neighbours = set(self.edges[subgraph_id].keys()) | set(self.edges[neighbour_id].keys())
        for neigh in all_neighbours:
            left_to_edges = []
            left_from_edges = []
            if neigh in self.edges[subgraph_id]:
                left_to_edges = self.edges[subgraph_id][neigh]
                left_from_edges = self.edges[neigh][subgraph_id]
            right_to_edges = []
            right_from_edges = []
            if neigh in self.edges[neighbour_id]:
                right_to_edges = self.edges[neighbour_id][neigh]
                right_from_edges = self.edges[neigh][neighbour_id]
            to_edges = self.merge_sorted_lists(left_to_edges, right_to_edges)
            from_edges = self.merge_sorted_lists(left_from_edges, right_from_edges)
            self.edges[neigh][new_graph.id] = from_edges
            self.edges[new_graph.id][neigh] = to_edges

        self.subgraphs[new_graph.id] = new_graph
        self.subgraphs_order.add(new_graph.id)
        for other_id in self.edges[subgraph_id]:
            del(self.edges[other_id][subgraph_id])
        for other_id in self.edges[neighbour_id]:
            del(self.edges[other_id][neighbour_id])
        del(self.edges[subgraph_id])
        del(self.edges[neighbour_id])
        del(self.subgraphs[subgraph_id])
        del(self.subgraphs[neighbour_id])
        self.merged += [neighbour_id, subgraph_id]
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
        result += l1[i:] + l2[j:]
        return result

    def distance_matrix(self):
        subgraphs_cnt = len(self.subgraphs)
        dist_mat = np.ndarray(shape=(subgraphs_cnt, subgraphs_cnt), dtype=np.float_)
        dist_mat.fill(float("inf"))
        np.fill_diagonal(dist_mat, 0.0)

        subgraphs_keys = self.subgraphs.keys()
        for index, key in enumerate(subgraphs_keys):
            for index2, key2 in enumerate(subgraphs_keys):
                if index == index2:
                    continue

                if key2 in self.edges[key]:
                    dist_mat[index, index2] = self.edges[key][key2]

        for index_w, w in enumerate(subgraphs_keys):
            for index_v1, v1 in enumerate(subgraphs_keys):
                for index_v2, v2 in enumerate(subgraphs_keys):
                    if v1 == v2 or v1 == w or v2 == w:
                        continue
                    v1w = dist_mat[index_v1, index_w]
                    wv2 = dist_mat[index_w, index_v2]
                    dist_mat[index_v1, index_v2] = min(dist_mat[index_v1, index_v2], v1w + wv2)

        self.edges = {}
        self.distance_matrix = dist_mat
        for sg in self.subgraphs:
            self.subgraphs[sg].distance_matrix()

    def pickle_graph(self, path):
        with open(path + 'graph' + str(self.id) + '.p', 'wb') as f:
            pickle.dump( (self.distance_matrix, self.subgraphs.keys()), f)
        for sg in self.subgraphs:
            self.subgraphs[sg].pickle_graph(path)
