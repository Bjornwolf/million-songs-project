import yaml
from recommender import Recommender
import sys
import json


def prettyprint_song(config_dict, fname):
    json_loc = '/'.join([fname[2], fname[3], fname[4], fname]) + '.json'
    json_loc = config_dict['data_path'] + json_loc
    json_dict = json.load(open(json_loc))
    print json_dict['artist'], ' -- ', json_dict['title']
    print json_dict['tags']


def run():
    config_dict = yaml.load(open(sys.argv[1], 'r'))
    uniq = config_dict['uniq_map_file']
    runiq = config_dict['runiq_map_file']
    path = config_dict['pickle_dir']
    rec = Recommender(path, uniq, runiq)
    ch = []
    user = rec.generate_user()
    ch = rec.recommend(user, n=5)
    for fname in user:
        prettyprint_song(config_dict, fname)
    print user, ' --> ', ch
    # prettyprint_song(config_dict, name)
    print '-->'
    for fname in ch:
        prettyprint_song(config_dict, fname)
run()
