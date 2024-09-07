import copy
import random
from .distance import tsp
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
    
    # print(params["repeat_count"], " 번째 tsp 결과")
    # for place in path:
    #     print(place["name"])
    
    visited = [False] * len(place_list)    
    
    # 점수 합 계산 + 이미 간 관광지 처리 ( idx_list에는 그리디에서 넣은 관광지만 있음, 숙소 및 필수 여행지 없음 )
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
        target_idx = random.randint(0, len(path) - 1)
        limit = 0
        
        # 이전 버전은 그리디에서 만들어진 idx_list를 기준으로 하기에 필수여행지, 숙소를 없애버린다는 문제가 있었음
        
        # 바꿀 관광지 탐색 - 기존 place_list에서 path로 변경
        while path[target_idx]["is_essential"] and limit < 10:
            target_idx = random.randint(0, len(path) - 1)
            limit += 1
        # 바꿀 수 있는 관광지를 찾지 못했을 경우
        if path[target_idx]["is_essential"]:
            continue
        
        # 바꿀 관광지 탐색 - 기존 place_list에서 place_score_list_not_in_path로 변경
        switch_idx = random.randint(0, len(place_score_list_not_in_path) - 1)
        while visited[switch_idx]:
            switch_idx = random.randint(0, len(place_score_list_not_in_path) - 1)
        
        
        new_path = copy.deepcopy(path)
        
        target_place = copy.deepcopy(new_path[target_idx])
        del new_path[target_idx]
        
        # idx_list 내의 백업값을 path를 직접 연결지을 수 없어서, place_score_list 내에 있는 값을 백업해둠
        target_place_score_idx = place_score_list()
        
        switch_place = copy.deepcopy(place_score_list_not_in_path[switch_idx])
        # 여기서 안지우고, 나중에 개선이 될 경우에만 지움
        #del place_score_list_not_in_path[switch_idx]
        #place_list_not_in_path[place_score_list_not_in_path[switch_idx][1]] = None
        
        new_path.insert(target_idx, switch_place)
        
        new_path, new_distance = tsp(new_path)
        new_distance_score = get_distance_score(new_distance, params)
        
        new_score = 0
        
        for idx in idx_list:
            new_score += idx[0]
        new_score -= new_distance_score

        # 점수 합 계산 + 이미 간 관광지 처리 ( idx_list에는 그리디에서 미리 넣은 관광지만 있음 )
        #for idx in idx_list:
        #   score += idx[0]
        #  visited[idx[1]] = True
        
        
        if new_score > cur_score:
            print("힐클라이밍 개선 성공", new_score, cur_score)
            cur_score = new_score
            path = new_path
            switch_time = 0
            visited[switch_idx] = True
            visited[idx_list[target_idx][1]] = False
        else:
            idx_list[target_idx] = prev_idx
        
        # TODO 새로운 관광지를 넣어서 시간이 넘치는 경우 처리 해줘야함
        
    return path, idx_list, params["enough_place"]

