import numpy as np
import copy
import pprint
from .hill_climb import hill_climb
from ..common.constant import RESULT_NUM, CAR_TRANSIT, PUBLIC_TRANSIT
from .place_score import get_place_score_list

pp = pprint.PrettyPrinter()

def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_list, n_day, distance_sensitivity, transit, bandwidth):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)


    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum)
    #이때까지는 list의 인덱스가 list 에서 id

    path = []
    for t in range(RESULT_NUM):
        params = {"n_day": n_day, "distance_sensitivity": distance_sensitivity, "transit": transit,
                  "distance_bias": distance_bias[t]}
        place_score_list[t] = sorted(place_score_list[t], key=lambda x: x[0])
        result = route_search_repeat(place_list, place_score_list[t], accomodation_list, essential_place_list, time_limit_list, params, bandwidth)
        path.append(result)

    result = []
    while path:
        a = path.pop()
        if a not in path:
            result.append(a)
    return result

def route_search_repeat(place_list, place_score_list, accomodation_list, essential_place_list, time_limit_list, params, bandwidth):
    n_day = params["n_day"]


    place_score_list_copy = copy.deepcopy(place_score_list)

    path_day = []
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
        if bandwidth:
            time_limit -= 60

        #각 날짜별 시간 계산하는 부분 종료

        result = route_search_for_one_day(accomodation_list[i], accomodation_list[i + 1],place_list, place_score_list_copy, essential_place_list, time_limit, params)
        path_day.append(result)
    return path_day

def route_search_for_one_day(accomodation1, accomodation2, place_list, place_score_list, essential_place_list, time_limit, params):
    transit = params["transit"]
    path = []
    time_coast = 0
    score_sum = 0
    place_idx_list = []
    if not accomodation1["is_dummy"]:
        path.append(accomodation1)
        time_coast += accomodation1["taken_time"]
    for essential in essential_place_list:
        if not essential["is_dummy"]:
            path.append(essential)
            time_coast += essential["taken_time"]
    popper = len(place_score_list) - 1
    while time_limit > time_coast and len(place_score_list) > 0 and len(path) < 5 and popper >= 0:
        place_idx = place_score_list[popper]
        popper -= 1
        place = place_list[place_idx[1]]

        if time_coast + place["taken_time"] <= time_limit:
            path.append(place)
            score_sum += place_idx[0]
            place_idx_list.append(place_idx)
            time_coast += place["taken_time"]

    # 240123 - 하루 일정 마친 후의 숙소를 추가 -> TODO 힐클라임에도 고려하여 수정해야함
    if not accomodation2["is_dummy"]:
        path.append(accomodation2)
        time_coast += accomodation2["taken_time"]  #숙소인데 왜 소요시간이 있냐. 이동시간이면 몰라도

    path, idx_list = hill_climb(place_list, place_score_list, place_idx_list, path, params)

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
            time_coast -= place["taken_time"]

    return path
