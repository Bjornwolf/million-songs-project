import glob
import json
import math
import gc
import pickle

def load_data(data_set_glob, uniq_map_file, runiq_map_file):
    train_files = glob.glob(data_set_glob)
    uniq_number = 0
    uniq_map = {}
    vertices_map = {}

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        if track["track_id"] in uniq_map:
            track["track_id"] = uniq_map[track["track_id"]]
        else:
            uniq_map[track["track_id"]] = uniq_number
            track["track_id"] = uniq_number
            uniq_number += 1

        for index, similar in enumerate(track["similars"]):
            tid, _ = similar
            if tid in uniq_map:
                track["similars"][index][0] = uniq_map[tid]
            else:
                uniq_map[tid] = uniq_number
                track["similars"][index][0] = uniq_number
                uniq_number += 1
            track["similars"][index][1] = 1.0 / track["similars"][index][1]

        del(track['tags'])
        new_similars = {}
        for edge in track['similars']:
            new_similars[edge[0]] = edge[1]
        new_track = {}
        for key in track:
            new_track[key] = track[key]
        new_track['similars'] = new_similars
        del(track)
        vertices_map[new_track['track_id']] = new_track
        handler.close() 

    with open(uniq_map_file, "wb") as f:
        pickle.dump(uniq_map, f)

    with open(runiq_map_file, "wb") as f:
        pickle.dump({ v: k for k, v in uniq_map.items() }, f)

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
        vs = vertices_map[key]['similars'].keys()
        for v in vs:
            if v not in vertices_map:
                del(vertices_map[key]['similars'][v])
        if len(vertices_map[key]['similars']) == 0:
            deleted += 1
            del(vertices_map[key])

    return vertices_map, deleted
