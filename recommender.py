import cPickle as pickle
import numpy as np
import random

class Recommender(object):
    def __init__(self, path, uniq, runiq):
        self.known_vertices = {}
        self.path = path
        with open(path + 'toplevel.p') as f:
            self.toplevel = pickle.load(f)
        with open(uniq) as f:
            self.uniq = pickle.load(f)
        with open(runiq) as f:
            self.runiq = pickle.load(f)

    def generate_user(self, n=100):
        # wybierz piosenke poczatkowa
        song = None
        while not song:
            song = random.choice(self.uniq.keys())
            _, un, _ = self.locate_ids([self.uniq[song]])
            if len(un) != 0:
                song = None
        songs = [song]
        while len(songs) < n:
            recommended = self.recommend(songs, n=5)
            songs += recommended
        return songs
        # dopoki nie nazbierasz piose

    def recommend(self, liked_songs, n=10):
        ids = map(lambda x: self.uniq[x], liked_songs)
        ids_set = set(ids)
        found_ids, unfound_ids, neighbours = self.locate_ids(ids)
        result_dist = {}
        for name, value in neighbours:
            if name in ids_set or value < 0.5:
                continue
            else:
                if name not in result_dist:
                    result_dist[name] = 0.
                result_dist[name] += 1. / value
        result_keys = result_dist.keys()
        result_keys = map(lambda x: self.runiq[x], result_keys)
        result_values = np.array(result_dist.values())
        result_values /= result_values.sum()
        # for p in zip(result_keys, result_values):
            # print p

        chosen = []
        if len(result_values) > 0:
            while len(chosen) < n:
                result_values_cs = np.cumsum(result_values)
                rand = np.random.random()
                i = np.argmin(rand > result_values_cs)
                result_values[i] = 0.
                chosen.append(result_keys[i])
        return chosen
          

    def locate_ids(self, ids):
        total_neighbours = []
        total_found = []
        for graph_id in self.toplevel:
            found_ids, ids, neighbours = self.find_in_graph(graph_id, ids)
            total_found += found_ids
            total_neighbours += neighbours
        return total_found, ids, total_neighbours

    def find_in_graph(self, graph_id, ids):
        total_found_ids = []
        total_neighbours = []
        if graph_id >= 0:
            unfound = []
            for ident in ids:
                if ident == graph_id:
                    total_found_ids.append(graph_id)
                else:
                    unfound.append(ident)
            return total_found_ids, unfound, total_neighbours
        else:
            matrix, subgraphs = self.load_graph(graph_id)
            for (i, sg) in enumerate(subgraphs):
                found_ids, ids, neighbours = self.find_in_graph(sg, ids)
                total_found_ids += found_ids
                total_neighbours += neighbours
                if len(found_ids) > 0:
                    for (j, sg2) in enumerate(subgraphs):
                        sg2_vertices = self.all_vertices(sg2)
                        total_neighbours += [(v, matrix[i][j]) for v in sg2_vertices]
            return total_found_ids, ids, total_neighbours

    def all_vertices(self, graph_id):
        if graph_id >= 0:
            return [graph_id]
        if graph_id in self.known_vertices:
            return self.known_vertices[graph_id]
        _, subgraphs = self.load_graph(graph_id)
        vertices = []
        for sg in subgraphs:
            vertices += self.all_vertices(sg)
        self.known_vertices[graph_id] = vertices
        return vertices

    def load_graph(self, graph_id):
        name = self.path + 'graph' + str(graph_id) + '.p'
        with open(name) as f:
            return pickle.load(f)
