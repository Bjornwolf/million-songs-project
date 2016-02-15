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
        del(key['tags'])
        new_similars = {}
        for edge in key['similars']:
            new_similars[edge[0]] = edge[1]
        vertices_map[key['track_id']] = key
        vertices_map[key['track_id']]['similars'] = new_similars
    return vertices_map

def fix_similarity_symmetry(vertices_map):
    one_direction_edges = 0
    nonsymmetrical_edges = 0
    for v1_id in vertices_map:
        for v2_id in vertices_map[v1_id]['similars']:
            if v2_id not in vertices_map:
                continue
            v1_to_v2_cost = vertices_map[v1_id]['similars'][v2_id]
            if v1_id not in vertices_map[v2_id]['similars']:
                one_direction_edges += 1
                vertices_map[v2_id]['similars'][v1_id] = v1_to_v2_cost
            v2_to_v1_cost = vertices_map[v2_id]['similars'][v1_id]
            if math.fabs(v1_to_v2_cost - v2_to_v1_cost) >= 1e-4:
                nonsymmetrical_edges += 1
                best_cost = max(v1_to_v2_cost, v2_to_v1_cost)
                vertices_map[v1_id]['similars'][v2_id] = best_cost
                vertices_map[v2_id]['similars'][v1_id] = best_cost
    return one_direction_edges, nonsymmetrical_edges

def purge_invalid_vertices(vertices_map):
    deleted = 0
    for key in vertices_map.keys():
        similars = vertices_map[key]['similars']
        vs = vertices_map[key]['similars'].keys()
        for v in vs:
            if v not in vertices_map:
                del(vertices_map[key]['similars'][v])
        if len(vertices_map[key]['similars']) == 0:
            deleted += 1
            del(vertices_map[key])

    return vertices_map, deleted

