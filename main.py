import yaml
import sys
from load_data import load_data
from graph import dist, check_graph
import numpy as np
import matplotlib.pyplot as plt

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
train_path = config_dict['train_data_location']
test_path = config_dict['test_data_location']

train_data, train_tags, test_data, test_tags = load_data(train_path, test_path)
vertices = {}
for d in train_data:
    vertices[d['track_id']] = d
print len(vertices)
res = check_graph(vertices)
print len(res)

plt.hist(res)
plt.show()
