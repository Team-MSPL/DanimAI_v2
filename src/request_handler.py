from src.ai.routeSearch import route_search_main
from src.firebase.firebaseAccess import read_all_place
import numpy as np


def request_handler(regionList, accomodationList, selectList, essential_placeList, time_limit_array, n_day, transit, distance_sensitivity, bandwidth):
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
    route_search_main(place_list, place_feature_matrix, accomodationList, theme_matrix, essential_placeList, time_limit_array, n_day, distance_sensitivity, transit)
