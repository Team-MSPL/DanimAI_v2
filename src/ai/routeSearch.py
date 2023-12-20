import numpy as np
import copy
from src.common.constant import RESULT_NUM
from src.ai.place_score import get_place_score_list
def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit, n_day, distance_sensitvity, transit):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)

    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum)
    #이때까지는 list의 인덱스가 list 에서 id

    for t in range(RESULT_NUM):
        route_search_repeat(place_list, place_score_list[t], distance_bias[t], accomodation_list, essential_place_list, time_limit, n_day)

    # print(place_list)

def route_search_repeat(place_list, place_score_list, distance_bias, accomodation_list, essential_place_list, time_limit_list, n_day):
    # print(place_score_list)
    place_score_list_copy = copy.deepcopy(place_score_list)
    place_score_list_copy = sorted(place_score_list_copy, key=lambda x: x[0])
    path_day = []
    for i in range(n_day):
        route_search_for_one_day(accomodation_list[i], place_list, place_score_list_copy, distance_bias, essential_place_list, 100) #TODO time limit 알아오기


def route_search_for_one_day(accomodation, place_list, place_score_list, distance_bias, essential_place_list, time_limit):
    path = []
    time_coast = 0
    if accomodation == '':
        path.append(accomodation)
    while time_limit > time_coast and len(place_score_list) > 0:
        place = place_score_list.pop()
        place = place_list[place[1]]
        if time_coast + place["taken_time"] <= time_limit:
            path.append(place)
            time_coast += place["taken_time"]
    print(path)
