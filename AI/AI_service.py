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
    
    if version == 3:
        # 최대 길이 9 -> 11로 변경
        theme_matrix = np.array([
            select_list[0] + [0, 0, 0, 0],
            select_list[1] + [0, 0, 0, 0, 0],
            select_list[2] + [0, 0, 0, 0, 0],
            select_list[3],
            select_list[4] + [0, 0, 0, 0, 0, 0, 0]
        ], dtype=int)
    else:
        theme_matrix = np.array([
            select_list[0] + [0, 0],
            select_list[1] + [0, 0, 0],
            select_list[2],
            select_list[3] + [0],
            select_list[4] + [0, 0, 0, 0, 0]
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



async def recommend_handler(place_list, place_feature_matrix, select_list, transit, distance_sensitivity, lat, lng, version, page, page_for_place):
    
    all_zero_flag = True
    
    # 선택 안한 성향들을 -1로 수정하였음 TODO 결과값 비교해보기
    select_list_copy = copy.deepcopy(select_list)
    for idx, select in enumerate(select_list):
        for idx2, select_item in enumerate(select):
            if select_item == 0:
                # select_item 값을 바꾼다고 select_list 내의 값이 바뀌지는 않음 / 밖에서는 선언되지 않은 값이기에
                select_list[idx][idx2] = -1
            else:
                all_zero_flag = False  # 하나라도 있으면 all_zero가 아님
    
    if version == 3:
        # 최대 길이 9 -> 11로 변경
        theme_matrix = np.array([
            select_list[0] + [0, 0, 0, 0],
            select_list[1] + [0, 0, 0, 0, 0],
            select_list[2] + [0, 0, 0, 0, 0],
            select_list[3],
            select_list[4] + [0, 0, 0, 0, 0, 0, 0]
        ], dtype=int)
    else:
        theme_matrix = np.array([
            select_list[0] + [0, 0],
            select_list[1] + [0, 0, 0],
            select_list[2],
            select_list[3] + [0],
            select_list[4] + [0, 0, 0, 0, 0]
        ], dtype=int)

        
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)

    # 1-1. 전체 점수 계산
    place_score_matrix, distance_bias_matrix = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum, place_list, version)
    
    dist_coef = CAR_COEFF if transit == 0 else PUBLIC_COEFF
    
    # 랜덤으로 다양하게 추천 - TODO 어떤 가중치로 할지 결정?
    t = random.randint(0, RESULT_NUM - 1)
    place_score_list = copy.deepcopy(place_score_matrix[t])
    distance_bias = copy.deepcopy(distance_bias_matrix[t])
    
    # 1-2. 거리 계산
    if lat != 0.0 and lng != 0.0:
        for place in place_list:
            place["distance"] = haversine_distance(lat, lng, place['lat'], place['lng'])    # 실제 거리
        
        # 2. 관광지 점수를 "관광지 점수 - distance"로 수정
        for i in range(len(place_score_list)):
            index = place_score_list[i][1]  # 인덱스 가져오기
            
            # 여기서는, 좌표간 거리
            lat_diff = place_list[index]["lat"] - lat
            lon_diff = place_list[index]["lng"] - lng
            distance = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
            
            # all_zero_flag인 경우에도 인기도는 계산되므로, 거리순으로 정렬할때 인기도 배제해줘야함 - TODO 만약 인기도 + 거리를 계산해야 할 경우가 생기면 수정
            # 현재 거리순 = 위치 정보 O, 성향 정보 X - 일반적인 상황에서는 계절 성향이 기본으로 포함되기에 안걸림
            if all_zero_flag:
                place_score_list[i][0] = 0
            
            # 점수 수정            
            place_score_list[i][0] -= distance * (MAX_DISTANCE_SENSITIVITY - distance_sensitivity) * dist_coef * distance_bias
    
    # 2+. 관광지 점수 정규화 ( 50~100점 )
    scores = [score for score, _, _ in place_score_list]
    min_score = min(scores)
    max_score = max(scores)
    
    score_range = max_score - min_score if max_score != min_score else 1  # 분모 0 방지

    if not all_zero_flag:
        for i in range(len(place_score_list)):
            raw_score = place_score_list[i][0]
            #norm_score = (raw_score - min_score) / score_range * 100
            norm_score = (raw_score - min_score) / score_range * 50 + 50

            # 소숫점 제거: 정수로 변환 (반올림 또는 내림 선택 가능)
            norm_score = int(round(norm_score))  # 반올림
            #norm_score = int(norm_score)      # 버림

            place_score_list[i][0] = norm_score

            index = place_score_list[i][1]
            place_list[index]["score"] = norm_score  # 정수 점수로 갱신
        
    # 3. 관광지 점수가 높은 순으로 정렬 (내림차순)
    place_score_list = sorted(place_score_list, key=lambda x: -x[0])
    
    # 4. place_list도 동일한 순서로 정렬
    sorted_indices = [score[1] for score in place_score_list]  # 정렬된 인덱스 가져오기
    sorted_places = [place_list[idx] for idx in sorted_indices]
    place_list = copy.deepcopy(sorted_places)

    # 페이지네이션 적용
    start_idx = (page - 1) * page_for_place
    end_idx = start_idx + page_for_place
    paged_places = place_list[start_idx:end_idx]

    # 성향 계산 - 높은 성향 표기
    tendencyData = [
            ['힐링', '활동적인', '배움이 있는', '맛있는', '교통이 편한', '알뜰한'],
            ['레저 스포츠', '문화시설', '사진 명소', '이색체험', '유적지', '박물관', '공원', '사찰', '성지'],
            ['바다', '산', '드라이브', '산책', '쇼핑', '실내여행지', '시티투어', '전통'],
            ['나홀로', '연인과', '친구와', '가족과', '효도', '자녀와', '반려동물과'],
            #['봄', '여름', '가을', '겨울'],  # 계절 점수 제거 - TODO 수정 가능
        ];    
    if version == 3:
        tendencyData = [
                ['힐링', '활동적인', '배움이 있는', '맛있는', '교통이 편한', '알뜰한'],
                ['레저 스포츠', '산책', '드라이브', '이색체험', '쇼핑', '시티투어',],
                ['바다', '산', '실내여행지', '문화시설', '사진 명소', '유적지', '박물관', '전통', '공원', '사찰', '성지'],
                ['나홀로', '연인과', '친구와', '가족과', '효도', '자녀와', '반려동물과'],
                #['봄', '여름', '가을', '겨울'],  # 계절 점수 제거 - TODO 수정 가능
            ];
    
    for place in paged_places:
        # 계절 점수 제거 - TODO 수정 가능
        concept_list = [place['concept'], place['play'], place['tour'], place['partner']]
        
        select_list_mod = [select_list[1],select_list[2],select_list[3],select_list[0]]
        
        for i in range(len(select_list_mod)):
            for j in range(len(select_list_mod[i])):
                if select_list_mod[i][j] < 0:
                    select_list_mod[i][j] = 0.75
                
        # 각 성향 점수와 이름을 (이름, 점수) 형태로 모두 펼치기
        tendency_scores = []
        concept_list_select = sum_2d_arrays(select_list_mod, concept_list)
                
        for category_scores, category_labels in zip(concept_list_select, tendencyData):
            for score, label in zip(category_scores, category_labels):
                tendency_scores.append((label, score))
        
        # 점수 기준으로 정렬
        sorted_scores = sorted(tendency_scores, key=lambda x: -x[1])
        
        # 상위 점수 추출
        top_score = sorted_scores[0][1]
        top_candidates = [item for item in sorted_scores if item[1] == top_score]
        
        if len(top_candidates) >= 3:
            # 동점이 3개 이상이면 무작위로 3개 선택 - TODO 수정 가능
            topTendency = random.sample(top_candidates, 3)
        else:
            # 동점이 3개 미만이면, 순서대로 최대 3개까지 추출
            topTendency = sorted_scores[:3]
        
        # 결과 저장
        place['top_tendencies'] = [label for label, score in topTendency]  # 나중에 score 쓰려면 4/3 곱해야함


    return paged_places
    #return place_list
    #return place_list[:10]    # 상위 10개만 리턴


# 2차원 배열을 원소별로 합하는 함수
def sum_2d_arrays(arr1, arr2):
    result = []
    for row1, row2 in zip(arr1, arr2):
        # 각 행의 같은 인덱스에 있는 값끼리 합산
        result.append([x + y for x, y in zip(row1, row2)])
    return result