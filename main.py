import yaml
import sys

from graph import Graph
from load_data import load_data, vertices_map_from, purge_invalid_vertices
from analysis_stats import text_hist_clusters

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
data_location = config_dict['data_location']

data = load_data(data_location)

print "* Data loaded (%d entries)" % (len(data))
vertices_map = vertices_map_from(data)
print "* Vertices map generated"
purge_invalid_vertices(vertices_map)
print "* Cleaned up vertices map"

g = Graph(vertices_map)
g.reduce(min_elems=500)

print text_hist_clusters(g)

