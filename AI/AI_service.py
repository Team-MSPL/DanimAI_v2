from .ai.route_search import route_search_main
#from .firebase.firebaseAccess import FirebaseAccess
from .preprocess import preprocess
import numpy as np
import copy
import random
import math
import asyncio
from AI.resultStandardize import tendencyCalculate, standardize, getRanking
from .ai.place_score import get_place_score_list, haversine_distance
from .common.constant import CAR_COEFF, PUBLIC_COEFF, MAX_DISTANCE_SENSITIVITY, RESULT_NUM
from .logging_config import logger

async def request_handler(place_list, place_feature_matrix, accomodation_list, select_list, essential_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth, version):
    #fb = FirebaseAccess()
    
    #place_list, place_feature_matrix = fb.read_all_place(region_list, select_list, bandwidth)
    
    # 이미 비동기 처리 중인 이벤트 루프 내에서 asyncio.run() 불가능
    # # FirebaseAccess.read_all_place가 동기적이면 비동기로 변경해야 함
    # place_list, place_feature_matrix = asyncio.run(fb.read_all_place(region_list, select_list, bandwidth))
    
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
    
    if version == 3:
        # 최대 길이 9 -> 11로 변경
        theme_matrix = np.array([
            select_list[0] + [0, 0, 0, 0],
            select_list[1] + [0, 0, 0, 0, 0],
            select_list[2] + [0, 0, 0, 0, 0],
            select_list[3],
            select_list[4] + [0, 0, 0, 0, 0, 0, 0]
        ], dtype=int)

    # 선작업, Firebase 데이터 수집 + place 객체들 데이터 전처리
    place_list, place_feature_matrix, essential_place_list, accomodation_list = preprocess(place_list, essential_place_list, accomodation_list, place_feature_matrix, version)
    
    # route search 메인 부분 - 그리디, 힐클라이밍, 스코어링
    result, enough_place = route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_array, n_day, distance_sensitivity, transit, bandwidth, version)

    # 평균 점수 + 점수 보정 + 등수 계산         
    best_point_list = tendencyCalculate(result, select_list_copy, version)
    best_point_list = standardize(best_point_list)
    best_point_list = getRanking(best_point_list)
    # print(best_point_list)
    return result, best_point_list, enough_place



async def recommend_handler(place_list, place_feature_matrix, select_list, transit, distance_sensitivity, lat, lng, version):
    
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
    
    
    if version == 3:
        # 최대 길이 9 -> 11로 변경
        theme_matrix = np.array([
            select_list[0] + [0, 0, 0, 0],
            select_list[1] + [0, 0, 0, 0, 0],
            select_list[2] + [0, 0, 0, 0, 0],
            select_list[3],
            select_list[4] + [0, 0, 0, 0, 0, 0, 0]
        ], dtype=int)
        
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)

    # 1-1. 전체 점수 계산
    place_score_matrix, distance_bias_matrix = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum, place_list, version)
    
    # 1-2. 거리 계산
    for place in place_list:
        place["distance"] = haversine_distance(lat, lng, place['lat'], place['lng'])    # 실제 거리
        
    dist_coef = CAR_COEFF if transit == 0 else PUBLIC_COEFF
    
    # 랜덤으로 다양하게 추천 - TODO 어떤 가중치로 할지 결정?
    t = random.randint(0, RESULT_NUM - 1)
    place_score_list = copy.deepcopy(place_score_matrix[t])
    distance_bias = copy.deepcopy(distance_bias_matrix[t])
        
    # 2. 관광지 점수를 "관광지 점수 - distance"로 수정
    for i in range(len(place_score_list)):
        index = place_score_list[i][1]  # 인덱스 가져오기
        
        # 여기서는, 좌표간 거리
        lat_diff = place_list[index]["lat"] - lat
        lon_diff = place_list[index]["lng"] - lng
        distance = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
        # 점수 수정            
        place_score_list[i][0] -= distance * (MAX_DISTANCE_SENSITIVITY - distance_sensitivity) * dist_coef * distance_bias
        
        # 각 place 객체에 "관광지 점수" 추가
        place_list[index]["score"] = place_score_list[i][0]  # 관광지 점수 추가
    
    
    # 3. 관광지 점수가 높은 순으로 정렬 (내림차순)
    place_score_list = sorted(place_score_list, key=lambda x: -x[0])
    
    # 4. place_list도 동일한 순서로 정렬
    sorted_indices = [score[1] for score in place_score_list]  # 정렬된 인덱스 가져오기
    sorted_places = [place_list[idx] for idx in sorted_indices]
    place_list = copy.deepcopy(sorted_places)


    return place_list
    #return place_list[:10]    # 상위 10개만 리턴

