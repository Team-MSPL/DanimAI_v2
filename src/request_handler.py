from src.ai.routeSearch import route_search_main
from src.firebase.firebaseAccess import read_all_place
from preprocess import preprocess
import numpy as np


def request_handler(regionList, accomodation_list, selectList, essential_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth):
    place_list, place_feature_matrix = read_all_place(regionList, bandwidth)
    # for place in place_list:
    #     print(place)
    # for feature in place_feature_matrix:
    #     print(feature)
    theme_matrix = np.array([
        selectList[0] + [0, 0],
        selectList[1] + [0, 0, 0],
        selectList[2],
        selectList[3] + [0],
        selectList[4] + [0, 0, 0, 0, 0]
    ], dtype=int)
    place_list, essential_place_list, accomodation_list = preprocess(place_list, essential_place_list, accomodation_list)
    route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_array, n_day, distance_sensitivity, transit)
