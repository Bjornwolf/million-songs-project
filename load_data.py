import glob
import json
import math
import gc
import pickle

def load_data(data_set_glob):
    train_files = glob.glob(data_set_glob)
    uniq_number = 0
    uniq_map = {}
    vertices_map = {}

    for track_file in train_files:
        handler = open(track_file, 'r')
        track = json.load(handler)
        del(track["tags"])
        del(track["artist"])
        del(track["timestamp"])
        del(track["title"])

        uniq_map[track["track_id"]] = uniq_number
        track["track_id"] = uniq_number
        uniq_number += 1        
        vertices_map[track["track_id"]] = track
        handler.close()

    for key in vertices_map:
        to_delete = set() 
        track = vertices_map[key]
        for index, similar in enumerate(track["similars"]):
            tid, _ = similar
            if tid in uniq_map:
                track["similars"][index][0] = uniq_map[tid]
                track["similars"][index][1] = 1 / track["similars"][index][1]
            else:            
                to_delete.add(index)
        track["similars"] = [s for k, s in enumerate(track["similars"]) if k not in to_delete]

    for key in vertices_map:
        track = vertices_map[key]
        new_similars = {}
        for edge in track['similars']:
            new_similars[edge[0]] = edge[1]
        new_track = {}
        for key in track:
            new_track[key] = track[key]
        del(track)
        new_track['similars'] = new_similars
        vertices_map[new_track['track_id']] = new_track

    return vertices_map, { v: k for k, v in uniq_map.items() }                 

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


def purge_invalid_vertices(vertices_map, runiq_map, uniq_map_file, runiq_map_file):
    deleted = 0
    for key in vertices_map.keys():
        if len(vertices_map[key]['similars']) == 0:
            deleted += 1
            del(vertices_map[key])
            del(runiq_map[key])

    with open(runiq_map_file, "wb") as f:
        pickle.dump(runiq_map, f)

    with open(uniq_map_file, "wb") as f:
        pickle.dump({ v: k for k, v in runiq_map.items() }, f)

    return vertices_map, deleted
