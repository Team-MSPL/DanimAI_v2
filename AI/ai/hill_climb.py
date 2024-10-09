import copy
import random
from .distance import tsp
from ..common import constant

def get_distance_score(distance, params):
    sensitivity, transit, distance_bias = params['distance_sensitivity'], params['transit'], params['distance_bias']
    dist_coef = constant.CAR_COEFF if transit == 0 else constant.PUBLIC_COEFF
    return distance * (constant.MAX_DISTANCE_SENSITIVITY - sensitivity) * dist_coef * distance_bias

# def get_path_score(path):
def hill_climb(place_list, place_score_list_not_in_path, idx_list, path, params):
    score = 0
    
    # 먼저 한 번 경로 최적화
    path, distance = tsp(path)   
    
    # 점수 합 계산 + 이미 간 관광지 처리 ( idx_list에는 그리디에서 넣은 관광지만 있음, 숙소 및 필수 여행지 없음 )
    for idx in idx_list:
        score += idx[0]
        #visited[idx[1]] = True

    distance_score = get_distance_score(distance, params)
    cur_score = score - distance_score
    
    execute_time = 0
    switch_time = 0
    

    while execute_time < constant.HILL_LIMIT and switch_time < constant.HILL_SWITCH_LIMIT:
        execute_time += 1
        switch_time += 1
        limit = 0
        
        # 바꿀 관광지 탐색 - 기존 place_list에서 path로 변경
        target_idx = random.randint(0, len(path) - 1)
        
        while path[target_idx]["is_essential"] and limit < 10:
            target_idx = random.randint(0, len(path) - 1)
            limit += 1
        # 바꿀 수 있는 관광지를 찾지 못했을 경우
        if path[target_idx]["is_essential"]:
            continue
        
        # 바꿀 관광지 탐색 - 기존 place_list에서 place_score_list_not_in_path로 변경
        switch_idx = random.randint(0, len(place_score_list_not_in_path) - 1)
        
        new_path = copy.deepcopy(path)
        new_idx_list = copy.deepcopy(idx_list)
        
        switch_place_score_idx_name = copy.deepcopy(place_score_list_not_in_path[switch_idx])
        switch_place = copy.deepcopy(place_list[switch_place_score_idx_name[1]])
        
        
        # 중복 검사: 새로운 switch_place가 이미 path 또는 idx_list에 있는지 확인
        # if any(switch_place["name"] == path_place["name"] for path_place in new_path) or \
        # any(switch_place["name"] == idx[2] for idx in new_idx_list):
        #     print("중복값 뽑읍 - 에러 - ", switch_place["name"])
        #     continue

        
        # new_path, new_idx_list를 새롭게 업데이트하는 부분
        target_place = copy.deepcopy(new_path[target_idx])
        del new_path[target_idx]
        
        # target_place 에 해당하는 장소를 기존 idx_list와 place_score_list_not_in_path 에서 제거하기 위함
        # new_idx_list - [점수계산결과, 인덱스, 관광지 이름] 형태
        target_place_score_idx_name = None
        for i, new_idx in enumerate(new_idx_list):
            if new_idx[2] == target_place["name"]:
                target_place_score_idx_name = copy.deepcopy(new_idx)
                del new_idx_list[i]  
                break
                
        new_idx_list.append(copy.deepcopy(switch_place_score_idx_name))
        new_path.insert(target_idx, copy.deepcopy(switch_place))
        # new_path, new_idx_list를 새롭게 업데이트하는 부분
        
        
        new_path, new_distance = copy.deepcopy(tsp(new_path))
        new_distance_score = get_distance_score(new_distance, params)
        
        new_score = 0
        
        for idx in new_idx_list:
            new_score += idx[0]
        
        new_score -= new_distance_score            
            
        if new_score > cur_score:
            # print("힐클라이밍 개선 성공", new_score, cur_score)    
            
            # 경로와 점수 리스트 업데이트
            cur_score = new_score
            path = copy.deepcopy(new_path)
            idx_list = copy.deepcopy(new_idx_list)

            # 관광지 리스트 업데이트
            del place_score_list_not_in_path[switch_idx]
            place_score_list_not_in_path.append(copy.deepcopy(target_place_score_idx_name))
            place_score_list_not_in_path.sort(key=lambda x: x[0])

            # 교체 성공 시 switch_time 초기화
            switch_time = 0
        
        
    
    return path, idx_list, params["enough_place"]

