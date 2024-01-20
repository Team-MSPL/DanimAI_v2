import numpy as np
import copy
import pprint
from src.ai.hill_climb import hill_climb
from src.common.constant import RESULT_NUM, CAR_TRANSIT, PUBLIC_TRANSIT
from src.ai.place_score import get_place_score_list

pp = pprint.PrettyPrinter()

def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_list, n_day, distance_sensitivity, transit):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)


    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum)
    #이때까지는 list의 인덱스가 list 에서 id


    for t in range(RESULT_NUM):
        params = {"n_day": n_day, "distance_sensitivity": distance_sensitivity, "transit": transit,
                  "distance_bias": distance_bias[t]}
        route_search_repeat(place_list, place_score_list[t], accomodation_list, essential_place_list, time_limit_list, params)

    # print(place_list)

def route_search_repeat(place_list, place_score_list, accomodation_list, essential_place_list, time_limit_list, params):
    # print(place_score_list)
    n_day = params["n_day"]

    place_score_list_copy = copy.deepcopy(place_score_list)
    #TODO 복사하여 반복하기 전에 정렬 한 번만 하고 복사해도 될듯?
    place_score_list_copy = sorted(place_score_list_copy, key=lambda x: x[0])
    path_day = []

    for i in range(n_day):
        time_limit = 840
        if i == 0:
            time_limit -= 60 * time_limit_list[0]
        elif i == n_day - 1:
            time_limit = 60 * time_limit_list[1]
        print("day: ", i + 1)
        route_search_for_one_day(accomodation_list[i], place_list, place_score_list_copy, essential_place_list, time_limit, params)


def route_search_for_one_day(accomodation, place_list, place_score_list, essential_place_list, time_limit, params):
    transit = params["transit"]
    path = []
    time_coast = 0
    score_sum = 0
    place_idx_list = []
    if not accomodation["is_dummy"]:
        path.append(accomodation)
        time_coast += accomodation["taken_time"]
    for essential in essential_place_list:
        if not essential["is_dummy"]:
            path.append(essential)
            time_coast += essential["taken_time"]
    popper = len(place_score_list) - 1
    while time_limit > time_coast and len(place_score_list) > 0 and len(path) < 5:
        place_idx = place_score_list[popper]
        popper -= 1
        place = place_list[place_idx[1]]
        if time_coast + place["taken_time"] <= time_limit:
            path.append(place)
            score_sum += place_idx[0]
            place_idx_list.append(place_idx)
            time_coast += place["taken_time"]

    path, idx_list = hill_climb(place_list, place_score_list, place_idx_list, path, params)

    moving_transit = CAR_TRANSIT if transit == 0 else PUBLIC_TRANSIT
    moving_time = (len(path) - 1) * moving_transit
    while moving_time + time_coast > time_limit and len(path) > 1:
        place = path.pop()
        idx = place_idx_list.pop()
        score_sum -= idx[0]
        time_coast -= place["taken_time"]
        moving_transit -= moving_transit

    pp.pprint(path)
