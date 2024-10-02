from .ai.route_search import route_search_main
from .firebase.firebaseAccess import FirebaseAccess
from .preprocess import preprocess
import numpy as np
import copy
from AI.resultStandardize import tendencyCalculate, standardize, getRanking

def request_handler(region_list, accomodation_list, select_list, essential_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth):
    fb = FirebaseAccess()
    place_list, place_feature_matrix = fb.read_all_place(region_list, select_list, bandwidth)
    
    # 선택 안한 성향들을 -1로 수정하였음 TODO 결과값 비교해보기
    select_list_copy = copy.deepcopy(select_list)
    for idx, select in enumerate(select_list):
        for idx2, select_item in enumerate(select):
            if select_item == 0:
                # select_item 값을 바꾼다고 select_list 내의 값이 바뀌지는 않음 / 밖에서는 선언되지 않은 값이기에
                select_list[idx][idx2] = -1
    
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
    result, enough_place = route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_array, n_day, distance_sensitivity, transit, bandwidth)

    # 평균 점수 + 점수 보정 + 등수 계산 
    best_point_list = tendencyCalculate(result, select_list_copy)
    best_point_list = standardize(best_point_list)
    best_point_list = getRanking(best_point_list)
    # print(best_point_list)
    return result, best_point_list, enough_place

