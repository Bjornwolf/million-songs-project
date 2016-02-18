import yaml
from recommender import Recommender
import sys
import random
import json


def prettyprint_song(config_dict, fname):
    json_loc = '/'.join([fname[2], fname[3], fname[4], fname]) + '.json'
    json_loc = config_dict['data_path'] + json_loc
    json_dict = json.load(open(json_loc))
    print json_dict['artist'], ' -- ', json_dict['title']
    # print json_dict['tags']

# @profile
def run():
    config_dict = yaml.load(open(sys.argv[1], 'r'))
    uniq = config_dict['uniq_map_file']
    runiq = config_dict['runiq_map_file']
    path = config_dict['pickle_dir']
    
    rec = Recommender(path, uniq, runiq)
    ch = []
    while len(ch) == 0:
        name = random.choice(rec.uniq.keys())
        ch = rec.recommend([name], n=5)
    print name, ' --> ', ch
    prettyprint_song(config_dict, name)
    print '-->'
    for fname in ch:
        prettyprint_song(config_dict, fname)
run()
