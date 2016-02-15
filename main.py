from example_graph import EXAMPLE_GRAPH
from graph import Graph
from load_data import load_data
import yaml
import sys
import matplotlib.pyplot as plt
from collections import Counter

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
data_location = config_dict['data_location']

train_data = load_data(train_path)

print "* Data loaded (%d entries)" % (len(train_data))
train_vertices_map = {}
for v in train_data:
    train_vertices_map[v['track_id']] = v

print "* Train vertices map generated"
# Clearing out vertices existing in similars, but not in dataset.
for v in train_vertices_map:
    similars = train_vertices_map[v]['similars']
    is_internal = lambda x: x[0] in train_vertices_map 
    train_vertices_map[v]['similars'] = filter(is_internal, similars)

print "* Cleaned up vertices map"
def similars_hist(train_vertices_map):
    counts = []
    for v in train_vertices_map:
        counts.append(len(train_vertices_map[v]['similars']))
    plt.hist(counts, bins=40)
    plt.show()

g = Graph(train_vertices_map)
g.reduce(min_elems=500)

clusters = []

def count_clusters(vertices, clusters):
    clusters.append(len(vertices))

    for v in vertices:
        if hasattr(vertices[v], 'vertices'):
            count_clusters(vertices[v].vertices, clusters)

count_clusters(g.vertices, clusters)
clusters = [len(g.vertices[x].vertices) for x in g.vertices]
print Counter(clusters)

