from graph import NewGraph
from collections import deque, Counter


class Forest(object):
    def __init__(self, vertices_map, min_graph_elems=500):
        self.vertices_map = vertices_map
        self.min_graph_elems = min_graph_elems

    def build_connected_components(self):
        used = [False] * (max(self.vertices_map.keys()) + 1)
        print "dzierzak"
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
                    if not used[nv]:
                        used[nv] = True
                        bfs_q.append(nv)
            print "nastepna skladowa"
            result.append(connected_component_keys)
            print len(result)
        return result

    def build_forest(self, connected_components):
        self.elements = []
        for connected_component in connected_components:
            self.elements.append(NewGraph({k: self.vertices_map[k] for k in
                                 connected_component}))

    def elements_count(self):
        return len(self.elements)

    def elements_size_hist(self):
        return Counter(map(lambda x: len(x.vertices), self.elements))

    def reduce(self):
        for graph in self.elements:
            graph.reduce(min_elems=self.min_graph_elems)
