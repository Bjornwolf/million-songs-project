from graph import Graph, FlatGraph
from collections import deque, Counter


class Forest(object):
    def __init__(self, vertices_map, min_graph_elems=500):
        self.vertices_map = vertices_map
        self.min_graph_elems = min_graph_elems

    def build_connected_components(self):
        used = [False] * (max(self.vertices_map.keys()) + 1)
        result = []

        for v in self.vertices_map:
            if used[v]:
                continue

            connected_component_keys = []
            bfs_q = deque([v])
            while len(bfs_q) != 0:
                pv = bfs_q.popleft()
                used[pv] = True
                connected_component_keys.append(pv)
                for nv in self.vertices_map[pv]['similars']:
                    if nv >= len(used):
                        print nv, len(used)
                    if not used[nv]:
                        bfs_q.append(nv)

            result.append(connected_component_keys)
        return result

    def build_forest(self, connected_components):
        self.elements = []
        for connected_component in connected_components:
            graph_type = Graph
            if len(connected_component) < self.min_graph_elems:
                graph_type = FlatGraph
            self.elements.append(graph_type({k: self.vertices_map[k] for k in
                                 connected_component}))

    def elements_count(self):
        return len(self.elements)

    def elements_size_hist(self):
        return Counter(map(lambda x: len(x.vertices), self.elements))

    def reduce(self):
        for graph in self.elements:
            graph.reduce(min_elems=self.min_graph_elems)
