import numpy as np
import copy
import pprint
from .hill_climb import hill_climb
from .distance import tsp
from .initialize_greedy import initialize_greedy
from ..common.constant import RESULT_NUM, CAR_TRANSIT, PUBLIC_TRANSIT
from .place_score import get_place_score_list




pp = pprint.PrettyPrinter()

def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_list, n_day, distance_sensitivity, transit, bandwidth):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)
    
    
    # 관광지 갯수 충분한지 - 한 번이라도 부족하면 False로 전환
    enough_place = True

    # 미리 스코어 계산하여 리스트화 + distance_bias는 원래 코드 123줄 즈음에 있는 ((10 - distanceSensitivityInAI) * 15) * sumForDistance를 계산한 것
    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum)
    #이때까지는 list의 인덱스가 list 에서 id

    path_list = []

    # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
    for t in range(RESULT_NUM):
        
        # 현재가 몇 번째 반복인지 반복문 안으로 넣어 줌
        repeat_count = t
        
        params = {"n_day": n_day, "distance_sensitivity": distance_sensitivity, "transit": transit, "distance_bias": distance_bias[t], "repeat_count":repeat_count, "bandwidth":bandwidth, "enough_place":enough_place, "move_time": 60 if distance_sensitivity < 6 else 30}
        
        # place_score_list 미리 정렬하기
        place_score_list[t] = sorted(place_score_list[t], key=lambda x: x[0])
        
        # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
        # deepcopy를 이용하여 각 반복별로 이미 경로에 들어간 관광지를 따로따로 제거
        result, enough_place = route_search_repeat(copy.deepcopy(place_list), copy.deepcopy(place_score_list[t]), copy.deepcopy(accomodation_list), copy.deepcopy(essential_place_list), time_limit_list, params)

        path_list.append(result)


    # 코스 중복 제거
    result = []
    
    while path_list:
        a = path_list.pop()  # 리스트에서 하나의 경로를 꺼냄
        # 다른 경로와 중복되지 않으면 결과에 추가
        if all(not np.array_equal(a, b) for b in path_list):  # path에 남아 있는 모든 경로와 비교
            result.append(a)
            
    
    print("최종 리턴하는 코스 수 : ", len(result))

    return result, enough_place

def route_search_repeat(place_list, place_score_list, accomodation_list, essential_place_list, time_limit_list, params):
    n_day = params["n_day"]


    place_score_list_copy = copy.deepcopy(place_score_list)
    
    # 갔던 장소를 또 가지 않게 하기 위함
    place_list_not_in_path = copy.deepcopy(place_list)
    place_score_list_not_in_path = copy.deepcopy(place_score_list)
    
    path_day = []
    
    # 날짜별 반복
    for i in range(n_day):

        #각 날짜별 시간 계산하는 부분 - 240123 보완
        time_limit = 540    #디폴트값
        if i == 0:
            time_limit = (18 - time_limit_list[0]) * 60
        elif i == n_day - 1:
            time_limit = (time_limit_list[1] - 10) * 60

        # 당일치기여행이면, time_limit_list[0]~time_limit_list[1]만 생각하면 된다.
        if n_day == 1:
            time_limit = time_limit_list[1] - time_limit_list[0]

            #당일치기라도, 점심 및 저녁 시간이 있으니, 제외하고 계산하기 위함
            time_limit = time_limit - 2 if time_limit > 6 else time_limit - 1

            time_limit = time_limit * 60
        
        # 여유로운 여행이면, 60분 줄이기
        if params["bandwidth"]:
            time_limit -= 60

        #각 날짜별 시간 계산하는 부분 종료

        result, enough_place = route_search_for_one_day(accomodation_list[i], accomodation_list[i + 1], place_list, place_list_not_in_path, place_score_list_copy, place_score_list_not_in_path, essential_place_list, time_limit, params, i)
        path_day.append(result)
        
        
    return path_day, enough_place

def route_search_for_one_day(accomodation1, accomodation2, place_list, place_list_not_in_path, place_score_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day):
    transit = params["transit"]
        
    # 코스 초안을 만드는 그리디 알고리즘 부분
    path, time_coast, score_sum, place_idx_list, enough_place = initialize_greedy(accomodation1, place_list, place_list_not_in_path, place_score_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day)
        
    # 240123 - 하루 일정 마친 후의 숙소를 추가 -> TODO 힐클라임에도 고려하여 수정해야함
    if not accomodation2["is_dummy"]:
        path.append(accomodation2)
        time_coast += 30            # 숙소는 더이상 소요시간 x. 숙소까지 이동하는 시간 추가
        
    
    # 그리디 결과 프린트 - 평시에는 주석 처리할 것
    # print(params["repeat_count"], " 번째 그리디 결과")
    # for place in path:
    #     print(place["name"])
    
    # 남은 관광지가 없을 경우 힐클라이밍 건너뛰고 tsp만하고 리턴
    if len(place_score_list_not_in_path) <= 0:
        print("관광지가 부족할 경우 (???) / 관광지 갯수 : ", len(place_score_list))
        params["enough_place"] = False
        path, distance = tsp(path)
        return path, params["enough_place"]
        

    path, idx_list, enough_place = hill_climb(place_list, place_list_not_in_path, place_score_list_not_in_path, place_idx_list, path, params)

    # 힐 클라이밍 이후 시간 제한 이상으로 튀어버린 여행 코스 뒷부분부터 pop
    moving_transit = CAR_TRANSIT if transit == 0 else PUBLIC_TRANSIT
    moving_time = (len(path) - 1) * moving_transit
    popper = len(path)
    while moving_time + time_coast > time_limit and len(path) > 1 and popper > 0:
        popper -= 1
        if not path[popper]["is_essential"]:
            place = path.pop(popper)
            idx = place_idx_list.pop()
            score_sum -= idx[0]
            time_coast -= place["takenTime"]

    return path, enough_place