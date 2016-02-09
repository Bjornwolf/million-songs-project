from example_graph import EXAMPLE_GRAPH
from graph import Graph
from load_data import load_data
import yaml
import sys
import matplotlib.pyplot as plt

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
train_path = config_dict['train_data_location']
test_path = config_dict['test_data_location']
similarity_threshold = config_dict['similarity_threshold']

train_data, train_tags, test_data, test_tags = load_data(train_path, test_path,
        similarity_threshold)

train_vertices_map = {}
for v in train_data:
    train_vertices_map[v['track_id']] = v

# Clearing out vertices existing in similars, but not in dataset.
for v in train_vertices_map:
    similars = train_vertices_map[v]['similars']
    is_internal = lambda x: x[0] in train_vertices_map 
    train_vertices_map[v]['similars'] = filter(is_internal, similars)

def similars_hist(train_vertices_map):
    counts = []
    for v in train_vertices_map:
        counts.append(len(train_vertices_map[v]['similars']))
    plt.hist(counts, bins=40)
    plt.show()

similars_hist(train_vertices_map)
g = Graph(train_vertices_map)
g.reduce(min_elems=2)
print g.vertices
