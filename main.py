from example_graph import EXAMPLE_GRAPH
from graph import Graph
# config_dict = yaml.load(open(sys.argv[1], 'r'))
# print config_dict
# train_path = config_dict['train_data_location']
# test_path = config_dict['test_data_location']
# similarity_threshold = config_dict['similarity_threshold']

g = Graph(EXAMPLE_GRAPH)
g.reduce()
