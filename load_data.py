import glob
import json
import sys
import math

def load_data(data_set_glob):
    train_files = glob.glob(data_set_glob)
    train_data = []

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler) 
        train_data.append(track)
        handler.close()

    return train_data

def vertices_map_from(data):
    vertices_map = {}
    for key in data:
        vertices_map[key['track_id']] = key
    return vertices_map

def fix_similarity_symmetricity(vertices_map):
    fixed_records = 0
    unequal_records = 0    
    for v1key in vertices_map:
        v1 = vertices_map[v1key]
        for v1index, v1similar in enumerate(v1['similars']):
            v2key, v1v2similar = v1similar
            if v2key not in vertices_map:
                continue

            v2 = vertices_map[v2key]

            is_symmetric = False
            for v2index, v2similar in enumerate(v2['similars']):
                vskey, v2v1similar = v2similar
                if vskey != v1key:
                    continue
                else:
                    is_symmetric = True
                    vertices_map[v1key]['similars'][v1index] = [v2key, max(v1v2similar, v2v1similar)]
                    vertices_map[v2key]['similars'][v2index] = [v1key, max(v1v2similar, v2v1similar)]
                    if math.fabs(v1v2similar - v2v1similar) >= 0.0001:
                        unequal_records += 1

            if not is_symmetric:
                vertices_map[v2key]['similars'].append([v1key, v1v2similar])
                fixed_records += 1

    return fixed_records, unequal_records

def purge_invalid_vertices(vertices_map):
    to_delete = []
    vertices_to_delete = []
    for key in vertices_map:
        similars = vertices_map[key]['similars']
        is_internal = lambda x: x[0] in vertices_map 
        vertices_map[key]['similars'] = filter(is_internal, similars)
        if len(vertices_map[key]['similars']) == 0:
            vertices_to_delete.append(key)

    for v in vertices_to_delete:
        del vertices_map[v]

    return vertices_map, len(vertices_to_delete)

