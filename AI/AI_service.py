from .ai.route_search import route_search_main
from .firebase.firebaseAccess import FirebaseAccess
from .preprocess import preprocess
import numpy as np

def request_handler(region_list, accomodation_list, select_list, essential_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth):
    fb = FirebaseAccess()
    place_list, place_feature_matrix = fb.read_all_place(region_list, select_list, bandwidth)
    # for place in place_list:
    #     print(place)
    # for feature in place_feature_matrix:
    #     print(feature)
    theme_matrix = np.array([
        select_list[0] + [0, 0],
        select_list[1] + [0, 0, 0],
        select_list[2],
        select_list[3] + [0],
        select_list[4] + [0, 0, 0, 0, 0]
    ], dtype=int)
    place_list, essential_place_list, accomodation_list = preprocess(place_list, essential_place_list, accomodation_list)
    return route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_array, n_day, distance_sensitivity, transit, bandwidth)
