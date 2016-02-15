import glob
import json
import sys

def load_data(train_set_dir):
    train_files = glob.glob(train_set_dir)
    test_files = glob.glob(test_set_dir)

    train_data = []

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        if len(track["similars"]) == 0:
            continue
        
        train_data.append(track)
        handler.close()

    return train_data
