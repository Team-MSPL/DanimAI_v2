import numpy as np
import copy
import pprint
import time
from .hill_climb import hill_climb
from .distance import tsp
from .initialize_greedy import initialize_greedy
from ..common.constant import RESULT_NUM, CAR_TRANSIT, PUBLIC_TRANSIT
from .place_score import get_place_score_list
from .optimize_multi_day_path import optimize_multi_day_path
from .remove_intersections import remove_routes_with_intersections
import traceback
from ..logging_config import logger
from ..common.constant import OVER_TIME, UNDER_TIME

def hash_day(day):
    # 하루치 경로의 위도와 경도를 고유하게 표현하기 위해 해시값 생성
    return tuple((place['lat'], place['lng']) for place in day)


pp = pprint.PrettyPrinter()

def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_list, n_day, distance_sensitivity, transit, bandwidth):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)
    

    # 관광지 갯수 충분한지 - 한 번이라도 부족하면 False로 전환
    enough_place = True

    # 미리 스코어 계산하여 리스트화 + distance_bias는 원래 코드 123줄 즈음에 있는 ((10 - distanceSensitivityInAI) * 15) * sumForDistance를 계산한 것
    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum, place_list)
    #이때까지는 list의 인덱스가 list 에서 id

    path_list = []
    clustering_ok_list = [] # clustering이 잘 된 path면 True

    # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
    for t in range(RESULT_NUM):
        
        # 현재가 몇 번째 반복인지 반복문 안으로 넣어 줌
        repeat_count = t
        
        params = {"n_day": n_day, "distance_sensitivity": distance_sensitivity, "transit": transit, "distance_bias": distance_bias[t], "repeat_count":repeat_count, "bandwidth":bandwidth, "enough_place":enough_place, "move_time": 60 if distance_sensitivity < 6 else 30}
        
        # place_score_list 미리 정렬하기
        place_score_list[t] = sorted(place_score_list[t], key=lambda x: x[0])
        
        # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
        # deepcopy를 이용하여 각 반복별로 이미 경로에 들어간 관광지를 따로따로 제거
        result, enough_place, clustering_ok = route_search_repeat(copy.deepcopy(place_list), copy.deepcopy(place_score_list[t]), copy.deepcopy(accomodation_list), copy.deepcopy(essential_place_list), time_limit_list, params)

        path_list.append(result)
        clustering_ok_list.append(clustering_ok)
        
        
    # 클러스터링 잘 된 코스가 하나라도 있으면 안된 코스들은 제거
    if clustering_ok_list.count(True) > 1:
        len_path_list = len(path_list)
        path_list = [path for idx, path in enumerate(path_list) if clustering_ok_list[idx]]

        logger.info("클러스터링 잘 안된 코스들은 제거 : %s 개", str(len_path_list - len(path_list)))
    
    # 교차하는 지점이 있는 코스 제거
    path_list_without_intersections = remove_routes_with_intersections(path_list)
    
    # 해시를 사용하여 중복 제거
    result = []
    seen_hashes = set()

    while path_list_without_intersections:
        a = path_list_without_intersections.pop()  # 원래 경로를 pop하여 가져옴
        
        # 각 하루치 경로를 위도(lat) 기준으로 정렬
        sorted_a = [sorted(day, key=lambda place: place['lat']) for day in a]
        
        # 경로의 고유성을 해시값으로 표현하여 확인
        a_hash = tuple(hash_day(day) for day in sorted_a)
        
        # 고유한 해시값이 없는 경우만 결과에 추가
        if a_hash not in seen_hashes:
            seen_hashes.add(a_hash)
            result.append(copy.deepcopy(a))
    
    # 최종 결과 결과 프린트 - 평시에는 주석 처리할 것
    # for idx_result, path_result in enumerate(result):
    #    logger.info(f"최종 코스 결과 , {idx_result}")
    #     for idx, day_path_result in enumerate(path_result):
    #        logger.info(f"{idx + 1},  일차 최종 코스 결과 ")
    #         for place_result in day_path_result:
    #            logger.info(place_result["name"])
    
    logger.info("최종 리턴하는 코스 수 : %s", str(len(result)))


    return result, enough_place

def route_search_repeat(place_list, place_score_list, accomodation_list, essential_place_list, time_limit_list, params):
    n_day = params["n_day"]


    place_score_list_copy = copy.deepcopy(place_score_list)
    
    # 갔던 장소를 또 가지 않게 하기 위함
    place_score_list_not_in_path = copy.deepcopy(place_score_list)
    
    multi_day_path = []
    time_limit_final_list = []
    
    # 날짜별 반복
    for i in range(n_day):

        #각 날짜별 시간 계산하는 부분 - 240123 보완
        time_limit = 540    #디폴트값
        if i == 0:
            time_limit = (18 - time_limit_list[0]) * 60
        elif i == n_day - 1:
            time_limit = (time_limit_list[1] - 11) * 60

        # 당일치기여행이면, time_limit_list[0]~time_limit_list[1]만 생각하면 된다.
        if n_day == 1:
            time_limit = time_limit_list[1] - time_limit_list[0]

            #당일치기라도, 점심 및 저녁 시간이 있으니, 제외하고 계산하기 위함
            time_limit = time_limit - 2 if time_limit > 6 else time_limit - 1

            time_limit = time_limit * 60
        
        # # 여유로운 여행이면, 60분 줄이기
        # if params["bandwidth"]:
        #     time_limit -= 60
            
        time_limit_final_list.append(time_limit)

        #각 날짜별 시간 계산하는 부분 종료

        result, enough_place, place_score_list_not_in_path = route_search_for_one_day(accomodation_list[i], accomodation_list[i + 1], place_list, place_score_list_copy, place_score_list_not_in_path, essential_place_list, time_limit, params, i)

        # 각 날마다 장소 리스트를 깊은 복사: 각 날의 탐색은 독립적이어야 하므로, place_score_list_not_in_path를 각 날마다 깊은 복사해야 합니다.
        place_score_list_not_in_path_copy = copy.deepcopy(place_score_list_not_in_path)
        place_score_list_not_in_path = copy.deepcopy(place_score_list_not_in_path_copy)
        
        multi_day_path.append(copy.deepcopy(result))
        
        if not params["enough_place"]:
            if len(multi_day_path[-1]) == 0:
                multi_day_path.pop()
            break
        
    # 시간 제한이 너무 짧아 greedy 에서 관광지 추가 를 못한 경우 처리 - day_path 중 하나는 []
    # 빈 배열의 위치 저장
    empty_indices = [index for index, item in enumerate(multi_day_path) if item == []]

    # 빈 배열([])을 제거한 새로운 배열 생성
    filtered_multi_day_path = copy.deepcopy([item for item in multi_day_path if item != []])

    if len(filtered_multi_day_path) > 0:
        filtered_multi_day_path, clustering_ok = optimize_multi_day_path(filtered_multi_day_path, time_limit_final_list, params["move_time"], place_list, place_score_list_not_in_path)
        
    # 나중에 빈 배열을 같은 위치에 추가
    for index in empty_indices:
        if index == len(multi_day_path) - 1:
            filtered_multi_day_path.append([])
        else:
            filtered_multi_day_path.insert(index, [])
    
    return multi_day_path, enough_place, clustering_ok

def route_search_for_one_day(accomodation1, accomodation2, place_list, place_score_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day):
    transit = params["transit"]
    
    # 남은 관광지가 없을 경우 바로 리턴
    if len(place_score_list_not_in_path) <= 0:
        logger.info("관광지가 부족할 경우 (2) / 관광지 갯수 : ", len(place_score_list))
        params["enough_place"] = False
        return [], params["enough_place"], place_score_list_not_in_path
    
    # 코스 초안을 만드는 그리디 알고리즘 부분
    path, time_coast, score_sum, place_idx_list, enough_place = initialize_greedy(accomodation1, place_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day)
            
    # 그리디 결과 프린트 - 평시에는 주석 처리할 것
    # print(params["repeat_count"], " 번째 그리디 결과")
    # for place in path:
    #     print(place["name"])
        
    if not accomodation2["is_dummy"]:
        path.append(accomodation2)
        time_coast += 30            # 숙소는 더이상 소요시간 x. 숙소까지 이동하는 시간 추가
        
    
    # 남은 관광지가 없을 경우 힐클라이밍 건너뛰고 tsp만하고 리턴
    if len(place_score_list_not_in_path) <= 0:
        path, _ = tsp(path)
        return path, params["enough_place"], place_score_list_not_in_path
        
    
    # 시간 제한이 너무 짧아 greedy 에서 관광지 추가를 못한 경우 - 바로 리턴 -> path = []
    elif len(place_idx_list) == 0:
        logger.info("시간 제한이 너무 짧아 greedy 에서 관광지 추가를 못한 경우 - 바로 리턴")
        return path, enough_place, place_score_list_not_in_path
        
        
    path, idx_list, enough_place = copy.deepcopy(hill_climb(place_list, place_score_list_not_in_path, place_idx_list, path, params))
    
    # 힐 클라이밍 이후 시간 제한 이상으로 튀어버린 여행 코스 뒷부분부터 pop - TODO 어차피 전체 경로 최적화 후에 이 작업 한 번 더 하니까, 하단 TODO 해결될 때 까진 주석
    # moving_transit = CAR_TRANSIT if transit == 0 else PUBLIC_TRANSIT
    # #moving_time = (len(path) - 1) * moving_transit
    # popper = len(path)
    
    # # "is_accomodation" 값이 False인 장소들의 개수를 계산 - 아래 반복문에서 
    # non_accommodation_count = sum(1 for place in path if not place["is_accomodation"])
    
    # while time_coast > time_limit + OVER_TIME and popper > 0 and non_accommodation_count > 1:
    #     popper -= 1
    #     if not path[popper]["is_essential"]:
    #         place = path.pop(popper)
    #         idx = place_idx_list.pop()
    #         #moving_time = (len(path) - 1) * moving_transit
    #         score_sum -= idx[0]
    #         time_coast -= place["takenTime"]
    #         time_coast -= params["move_time"]
    #         non_accommodation_count -= 1
            
    #         # 관광지 점수 리스트도 업데이트 - 만약 같은 관광지 중복으로 뜨는 문제 생기면 여기 지울 것! - TODO 중복 문제 해결하고 이거 주석 풀 것
    #         #place_score_list_not_in_path.append(copy.deepcopy([idx[0],idx[1],idx[2]]))
    #         #place_score_list_not_in_path.sort(key=lambda x: x[0])

    return path, enough_place, place_score_list_not_in_path