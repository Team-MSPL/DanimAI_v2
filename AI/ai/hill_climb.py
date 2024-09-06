from .distance import tsp
import random
from ..common import constant

def get_distance_score(distance, params):
    sensitivity, transit, distance_bias = params['distance_sensitivity'], params['transit'], params['distance_bias']
    dist_coef = constant.CAR_COEFF if transit == 0 else constant.PUBLIC_COEFF
    return distance * (constant.MAX_DISTANCE_SENSITIVITY - sensitivity) * dist_coef * distance_bias

# def get_path_score(path):
def hill_climb(place_list, place_list_not_in_path, place_score_list, place_score_list_not_in_path, idx_list, path, params):
    score = 0
    
    # 먼저 한 번 경로 최적화
    path, distance = tsp(path)
    
    print(params["repeat_count"], " 번째 tsp 결과")
    for place in path:
        print(place["name"])
    
    
    visited = [False] * len(place_list)
    for idx in idx_list:
        score += idx[0]
        visited[idx[1]] = True

    distance_score = get_distance_score(distance, params)

    cur_score = score - distance_score
    execute_time = 0
    switch_time = 0
    while execute_time < constant.HILL_LIMIT and switch_time < constant.HILL_SWITCH_LIMIT:
        execute_time += 1
        switch_time += 1
        target_idx = random.randint(0, len(idx_list) - 1)
        limit = 0
        while place_list[target_idx]["is_essential"] and limit < 10:
            target_idx = random.randint(0, len(idx_list) - 1)
            limit += 1
        if place_list[target_idx]["is_essential"]:
            continue
        switch_idx = random.randint(0, len(place_list) - 1)
        while visited[switch_idx]:
            switch_idx = random.randint(0, len(place_list) - 1)
        prev_idx = idx_list[target_idx]
        idx_list[target_idx] = place_score_list[switch_idx]
        new_path = [place_list[i[1]] for i in idx_list]
        new_path, new_distance = tsp(new_path)
        new_distance_score = get_distance_score(new_distance, params)
        new_score = 0
        for idx in idx_list:
            new_score += idx[0]
        new_score -= new_distance_score
        if new_score > cur_score:
            cur_score = new_score
            path = new_path
            switch_time = 0
            visited[switch_idx] = True
            visited[idx_list[target_idx][1]] = False
        else:
            idx_list[target_idx] = prev_idx
    return path, idx_list, params["enough_place"]

