from .ai.route_search import route_search_main
from .firebase.firebaseAccess import FirebaseAccess
from .preprocess import preprocess
import numpy as np
from AI.resultStandardize import tendencyCalculate, standardize, getRanking

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

    # 선작업, Firebase 데이터 수집 + place 객체들 데이터 전처리
    place_list, essential_place_list, accomodation_list = preprocess(place_list, essential_place_list, accomodation_list)
    
    # route search 메인 부분 - 그리디, 힐클라이밍, 스코어링
    result = route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_array, n_day, distance_sensitivity, transit, bandwidth)

    # 전체 동선 최적화 추가하기

    # 평균 점수 + 점수 보정 + 등수 계산
    pathThemeList = tendencyCalculate(result, select_list)
    pathThemeList = standardize(pathThemeList)
    pathThemeList = getRanking(pathThemeList)
    # print(pathThemeList)
    return result, pathThemeList

