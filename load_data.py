import glob
import json
import sys

def load_data(data_set_glob):
    train_files = glob.glob(data_set_glob)
    train_data = []

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        if len(track["similars"]) == 0:
            continue
        
        train_data.append(track)
        handler.close()

    return train_data

def vertices_map_from(data):
    vertices_map = {}
    for v in data:
        vertices_map[v['track_id']] = v
    return vertices_map

def purge_invalid_vertices(vertices_map):
    to_delete = []
    vertices_to_delete = []
    for v in vertices_map:
        similars = vertices_map[v]['similars']
        is_internal = lambda x: x[0] in vertices_map 
        vertices_map[v]['similars'] = filter(is_internal, similars)
        if len(vertices_map[v]['similars']) == 0:
            vertices_to_delete.append(v)

    for v in vertices_to_delete:
        del vertices_map[v]

    return vertices_map

