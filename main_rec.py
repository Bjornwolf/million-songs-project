import yaml
from recommender import Recommender
import sys
import json


def prettyprint_song(config_dict, fname):
    json_loc = '/'.join([fname[2], fname[3], fname[4], fname]) + '.json'
    json_loc = config_dict['data_path'] + json_loc
    json_dict = json.load(open(json_loc))
    print json_dict['artist'], ' -- ', json_dict['title']

def aggregate_tags(config_dict, names):
    all_tags = {}
    nonempties = 0
    for name in names:
        json_loc = '/'.join([name[2], name[3], name[4], name]) + '.json'
        json_loc = config_dict['data_path'] + json_loc
        json_dict = json.load(open(json_loc))
        tags = json_dict['tags']
        if len(tags) != 0:
            nonempties += 1
            for tag in tags:
                if tag[0] not in all_tags:
                    all_tags[tag[0]] = 0.
                all_tags[tag[0]] += float(tag[1])
    for key in all_tags:
        all_tags[key] /= nonempties
    return all_tags


def compare_aggregators(agg1, agg2, threshold = 5.0):
    interesting_tags = []
    for key in agg1:
        if key in agg2:
            if agg1[key] < threshold or agg2[key] < threshold:
                interesting_tags.append((key, (agg1[key] + agg2[key]) / 2)) 

    avgsum = sum(map(lambda x: x[1], interesting_tags))
    ppbs = map(lambda x: (x[0], x[1] / avgsum), interesting_tags)
    gini_imp = reduce(lambda m, (t, p): m + (p * (1 - p)), ppbs, 0.0)

    print gini_imp

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
    print '-->'
    for fname in ch:
        prettyprint_song(config_dict, fname)
    agg1 = aggregate_tags(config_dict, user)
    agg2 = aggregate_tags(config_dict, ch)
    compare_aggregators(agg1, agg2)
run()
