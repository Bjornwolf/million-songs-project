import yaml
from load_data import load_data

config_dict = yaml.load(open(sys.argv[1], 'r'))
print config_dict
train_path = config_dict['train_data_location']
test_path = config_dict['test_data_location']

train_data, train_tags, test_data, test_tags = load_data(train_path, test_path)

