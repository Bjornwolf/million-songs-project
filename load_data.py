import glob
import json
import sys

def load_data(train_set_dir, test_set_dir, similarity_threshold):
    train_files = glob.glob(train_set_dir)
    test_files = glob.glob(test_set_dir)

    train_data = []
    train_tags = {}
    test_data = []
    test_tags = {}

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        track["similars"] = filter(lambda similar: similar[1] > similarity_threshold, track["similars"]) 
        train_data.append(track)
        if len(track["tags"]) == 0:
            if None not in test_tags:
                train_tags[None] = (0, [])
            train_tags[None][1].append(track)
        else:
            for tag in track["tags"]:
                if tag[0] not in train_tags:
                    train_tags[tag[0]] = (tag[1], [])
                train_tags[tag[0]][1].append(track)
        handler.close()

    for track_file in test_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        test_data.append(track)
        if len(track["tags"]) == 0:
            if None not in test_tags:
                test_tags[None] = (0, [])
            test_tags[None][1].append(track)
        else:
            for tag in track["tags"]:
                if tag[0] not in test_tags:
                    test_tags[tag[0]] = (tag[1], [])
                test_tags[tag[0]][1].append(track)
        handler.close()

    return (train_data, train_tags, test_data, test_tags)

if __name__ == "__main__":
    train_glob = sys.argv[1]
    test_glob = sys.argv[2]

    data = load_data(train_glob, test_glob)
    print data[0][0]
