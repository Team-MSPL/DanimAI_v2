import copy
import random
from .distance import tsp
from ..common import constant

def get_distance_score(distance, params):
    sensitivity, transit, distance_bias = params['distance_sensitivity'], params['transit'], params['distance_bias']
    dist_coef = constant.CAR_COEFF if transit == 0 else constant.PUBLIC_COEFF
    return distance * (constant.MAX_DISTANCE_SENSITIVITY - sensitivity) * dist_coef * distance_bias

# def get_path_score(path):
def hill_climb(place_list, place_list_not_in_path, place_score_list_not_in_path, idx_list, path, params):
    score = 0
    
    # 먼저 한 번 경로 최적화
    path, distance = tsp(path)
    
    #visited = [False] * len(place_list)    
    
    # 점수 합 계산 + 이미 간 관광지 처리 ( idx_list에는 그리디에서 넣은 관광지만 있음, 숙소 및 필수 여행지 없음 )
    for idx in idx_list:
        score += idx[0]
        #visited[idx[1]] = True

    distance_score = get_distance_score(distance, params)
    cur_score = score - distance_score
    
    execute_time = 0
    switch_time = 0
    
    try:
        before_climb = True
        while execute_time < constant.HILL_LIMIT and switch_time < constant.HILL_SWITCH_LIMIT:
            execute_time += 1
            switch_time += 1
            limit = 0
            
            target_idx = random.randint(0, len(path) - 1)
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
            
            
            new_path = copy.deepcopy(path)
            new_idx_list = copy.deepcopy(idx_list)
            
            switch_place_score_idx = copy.deepcopy(place_score_list_not_in_path[switch_idx])
            switch_place = copy.deepcopy(place_list_not_in_path[switch_place_score_idx[1]])
            
            target_place = copy.deepcopy(new_path[target_idx])
            del new_path[target_idx]
            
            # target_place 에 해당하는 장소를 기존 idx_list와 place_list_not_in_path, place_score_list_not_in_path 에서 제거하기 위함
            target_place_idx = -1
            target_place_score_idx = None
            for i, place in enumerate(place_list):
                if place["name"] == target_place["name"]:
                    target_place_idx = i
                    break
            for i, place_score_idx in enumerate(new_idx_list):
                if place_score_idx[1] == target_place_idx:
                    target_place_score_idx = copy.deepcopy(place_score_idx)
                    del new_idx_list[i]  
                    break
                    
            new_idx_list.append(switch_place_score_idx)
            new_path.insert(target_idx, switch_place)
            print("12312312412")
            print(switch_idx)
            print(switch_place_score_idx)
            print(switch_place["name"])     # 여기서 에러! 이게 None이란다
            print("12312312412")
            
            
            new_path, new_distance = tsp(new_path)
            print("oipoipiopio")
            new_distance_score = get_distance_score(new_distance, params)
            
            new_score = 0
            
            for idx in new_idx_list:
                new_score += idx[0]
            
            new_score -= new_distance_score
            
    
            print("place_list_not_in_path.count(None)1111111111111111")
            print(place_list_not_in_path.count(None))
            print(len(place_list_not_in_path))
            print(len(place_score_list_not_in_path))
            
            if new_score > cur_score:
                print("힐클라이밍 개선 성공", new_score, cur_score)         
                
                
                print("place_list_not_in_path.count(None)22222222222222222222")
                print(place_list_not_in_path[place_score_list_not_in_path[switch_idx][1]])
                
                # 바뀐 관광지 제거
                place_list_not_in_path[switch_place_score_idx[1]] = None
                del place_score_list_not_in_path[switch_idx]
                
    
                print(place_list_not_in_path.count(None))
                print(len(place_list_not_in_path))
                print(len(place_score_list_not_in_path))

                print(place_list_not_in_path[place_score_list_not_in_path[switch_idx][1]])
                print(place_list_not_in_path[target_place_score_idx[1]])
                        
                # 기존 관광지 추가
                place_score_list_not_in_path.append(target_place_score_idx)
                place_score_list_not_in_path = sorted(place_score_list_not_in_path, key=lambda x: x[0])
                place_list_not_in_path[target_place_score_idx[1]] = target_place
                
                cur_score = new_score
                path = new_path
                idx_list = new_idx_list   
                
                switch_time = 0
            
    
                print("place_list_not_in_path.count(None)22222222222222222222")
                print(place_list_not_in_path.count(None))
                print(len(place_list_not_in_path))
                print(len(place_score_list_not_in_path))

                print(place_list_not_in_path[target_place_score_idx[1]])

            #디버깅용
            before_climb = new_score > cur_score

            # TODO 새로운 관광지를 넣어서 시간이 넘치는 경우 처리 해줘야함
    except Exception as e:
        print("e")
        print(e)
        print(len(place_score_list_not_in_path))
        print(len(place_list_not_in_path))
        print(switch_idx)
        print(switch_place_score_idx)
        print(before_climb)
        print(new_score > cur_score)
        print("e")
        
    return path, idx_list, params["enough_place"]

