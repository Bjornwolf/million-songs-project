import yaml
from recommender import Recommender
import sys
import json
import math

import matplotlib.pyplot as plt


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


def compare_aggregators(agg1, agg2, threshold=5.0):
    mse_err = 0.0
    mde_err = 0.0
    counted_tags = 0
    for key in agg1.keys():
        if agg1[key] < threshold:
            del agg1[key]
    for key in agg2.keys():
        if agg2[key] < threshold:
            del agg2[key]

    for key in agg1:
        if key in agg2:
            mse_err += (agg1[key] - agg2[key]) ** 2
            mde_err += math.fabs(agg1[key] - agg2[key])
        else:
            mse_err += agg1[key] ** 2
            mde_err += agg1[key]
        counted_tags += 1

    for key in agg2:
        if key not in agg1:
            mse_err += agg2[key] ** 2
            mde_err += agg2[key]
            counted_tags += 1

    print "MSE: ", mse_err / counted_tags
    print "MDE: ", mde_err / counted_tags

    return mse_err / counted_tags, mde_err / counted_tags

def run():
    mse_hist = []
    mde_hist = []
    samples = 100
    config_dict = yaml.load(open(sys.argv[1], 'r'))
    uniq = config_dict['uniq_map_file']
    runiq = config_dict['runiq_map_file']
    path = config_dict['pickle_dir']
    rec = Recommender(path, uniq, runiq)
    for sample in range(samples):
        ch = []
        tags_in_agg1 = []
        tags_in_agg2 = []
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
        tags_in_agg1.append(len(agg1))
        tags_in_agg2.append(len(agg2))
        mde, mse = compare_aggregators(agg1, agg2)
        mde_hist.append(mde)
        mse_hist.append(mse)
        print "***************     SAMPLE %d" % (sample)

    _, (mse_plot, mde_plot) = plt.subplots(2)
    print float(sum(tags_in_agg1)) / len(tags_in_agg1)
    print float(sum(tags_in_agg2)) / len(tags_in_agg2)
    mse_plot.set_title("Mean Squared Error / Tags Hist")
    mde_plot.set_title("Manhattan Dist Error / Tags Hist")
    mse_plot.hist(mse_hist, bins=100)
    mde_plot.hist(mde_hist, bins=100)
    plt.savefig(config_dict['hist_path'])

run()
