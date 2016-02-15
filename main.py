import yaml
import sys

from load_data import load_data, vertices_map_from, purge_invalid_vertices, fix_similarity_symmetry

from analysis_stats import text_hist_clusters, similars_hist

from forest import Forest

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
data_location = config_dict['data_location']

data = load_data(data_location)

print "* Data loaded (%d entries)" % (len(data))
vertices_map = vertices_map_from(data)
broken, unequal = fix_similarity_symmetry(vertices_map)
print "* Fixed similarity relation symmetry (%d unidirected, %d unequal)" % (broken, unequal)

print "* Vertices map generated"
_, deleted = purge_invalid_vertices(vertices_map)
print "* Cleaned up vertices map (deleted %d isolated vertices)" % (deleted)

similars_hist(vertices_map)

if 'min_elems' in config_dict:
    forest = Forest(vertices_map, min_graph_elems=config_dict['min_elems'])
else:
    forest = Forest(vertices_map)
forest.build()
forest.reduce()

print len(forest.elements)
print forest.elements_size_hist()

