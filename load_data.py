import sys
import glob
import json

# Usage: python load_data.py "./lastfm_train/**/**/**/*.json" "./lastfm_test/**/**/**/*.json"

train_set_directory = sys.argv[1]
test_set_directory = sys.argv[2]

def load_data(train_set_dir, test_set_dir, verbose=True):
    train_files = glob.glob(train_set_dir)
    test_files = glob.glob(test_set_dir)

    train_data = []
    train_tags = {}
    test_data = []
    test_tags = {}

    if verbose:
        print 'Processing train dataset'

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        train_data.append(track)
        if len(track["tags"]) == 0:
            if None not in test_tags:
                train_tags[None] = (0, [])
            train_tags[None][1].append(track)
        for tag in track["tags"]:
            if tag[0] not in train_tags:
                train_tags[tag[0]] = (tag[1], [])
            train_tags[tag[0]][1].append(track)
        handler.close()

    if verbose:
        print 'Processed train dataset (', len(train_data), ' entries)'
        print 'Processing test dataset'

    for track_file in test_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        test_data.append(track)
        if len(track["tags"]) == 0:
            if None not in test_tags:
                test_tags[None] = (0, [])
            test_tags[None][1].append(track)

        for tag in track["tags"]:
            if tag[0] not in test_tags:
                test_tags[tag[0]] = (tag[1], [])
            test_tags[tag[0]][1].append(track)
        handler.close()

    if verbose:
        print 'Processed test dataset (', len(test_data), ' entries)'

    return (train_data, train_tags, test_data, test_tags)
