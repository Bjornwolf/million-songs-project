from graph import check_part

class DataClusters(object):
    def __init__(self):
        self.next_cluster_number = 0
        self.clusters = {}

    def process_dataset(self, vertices):
        unvisited_ids = set(vertices.keys())
        while len(unvisited_ids) != 0:
            candidate_id = unvisited_ids.pop()
            cluster_element_ids = check_part(candidate, vertices)
            cluster_elements = {}
            for element_id in cluster_element_ids:
                cluster_elements[element_id] = vertices[element_id]
            unvisited_ids -= cluster_element_ids
            self.next_cluster_number += 1
            self.clusters[self.next_cluster_number] = Cluster(cluster_element_ids, cluster_elements)

    def cluster_count(self):
        return len(self.clusters)

    def cluster_hist(self):
        hist = {}
        for number in self.clusters:
            hist[number] = self.clusters[number].size()
        return hist

class Cluster(object):
    def __init__(self, element_ids, cluster_elements):
        self.element_ids = element_ids
        self.cluster_elements = cluster_elements

    def size(self):
        return len(self.element_ids)
