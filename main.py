import yaml
import sys

from graph import Graph
from load_data import load_data
from collections import Counter

from stat import text_hist_clusters

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
data_location = config_dict['data_location']

data = load_data(data_location)

print "* Data loaded (%d entries)" % (len(data))
vertices_map = {}
for v in data:
    vertices_map[v['track_id']] = v

print "* Vertices map generated"
for v in vertices_map:
    similars = vertices_map[v]['similars']
    is_internal = lambda x: x[0] in vertices_map 
    vertices_map[v]['similars'] = filter(is_internal, similars)

print "* Cleaned up vertices map"

g = Graph(vertices_map)
g.reduce(min_elems=500)

print text_hist_clusters(g)

