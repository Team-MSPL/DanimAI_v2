import numpy as np
import copy
import pprint
import time
from .hill_climb import hill_climb
from .distance import tsp
from .initialize_greedy import initialize_greedy
from ..common.constant import RESULT_NUM, CAR_TRANSIT, PUBLIC_TRANSIT
from .place_score import get_place_score_list, normalize_scores, geo_efficiency, diversity_score, popularity_stats
from .optimize_multi_day_path import optimize_multi_day_path
from .remove_intersections import remove_routes_with_intersections
from .BO.optimize_weights import optimize_weights
import traceback
from ..logging_config import logger
from ..common.constant import OVER_TIME, UNDER_TIME
import traceback





def hash_day(day):
    # 하루치 경로의 위도와 경도를 고유하게 표현하기 위해 해시값 생성
    return tuple((place['lat'], place['lng']) for place in day)


pp = pprint.PrettyPrinter()

def route_search_main(place_list, place_feature_matrix, accomodation_list, theme_matrix, essential_place_list, time_limit_list, n_day, distance_sensitivity, transit, bandwidth, popular_sensitivity, version):
    selectedThemeNum_list = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNum_list)
    

    # 관광지 갯수 충분한지 - 한 번이라도 부족하면 False로 전환
    enough_place = True

    # 미리 스코어 계산하여 리스트화 + distance_bias는 원래 코드 123줄 즈음에 있는 ((10 - distanceSensitivityInAI) * 15) * sumForDistance를 계산한 것
    place_score_list, distance_bias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNum_list, activatedThemeNum, place_list, popular_sensitivity, version)
    #이때까지는 list의 인덱스가 list 에서 id

    path_list = []
    clustering_ok_list = [] # clustering이 잘 된 path면 True
    place_score_avg_list = []

    # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
    for t in range(RESULT_NUM):
        try:
            # 현재가 몇 번째 반복인지 반복문 안으로 넣어 줌
            repeat_count = t
            
            params = {"n_day": n_day, "distance_sensitivity": distance_sensitivity, "transit": transit, "distance_bias": distance_bias[t], "repeat_count":repeat_count, "bandwidth":bandwidth, "enough_place":enough_place, "move_time": 60 if distance_sensitivity < 6 else 30}
            
            # place_score_list 미리 정렬하기
            place_score_list[t] = sorted(place_score_list[t], key=lambda x: x[0])
            
            # RESULT_NUM만큼 반복하여 결과물 코스를 산출함 ( 이전 코드의 쓰레드 수 )
            # deepcopy를 이용하여 각 반복별로 이미 경로에 들어간 관광지를 따로따로 제거
            result, multi_day_place_idx_list, enough_place, clustering_ok = route_search_repeat(copy.deepcopy(place_list), copy.deepcopy(place_score_list[t]), copy.deepcopy(accomodation_list), copy.deepcopy(essential_place_list), time_limit_list, params)

            len_place_score_avg_list = len(place_score_avg_list)
            
            try:
                if len(multi_day_place_idx_list) == 0:
                    logger.error("multi_day_place_idx_list is empty, skipping average calculation.")
                    logger.error(accomodation_list)
                    logger.error(essential_place_list)
                    logger.error(theme_matrix)
                
                else:
                    values = [x[0] if len(x) > 0 else 0 for x in multi_day_place_idx_list]

                    # 평균 계산
                    average = sum(values) / len(values)

                    # logger.info("평균")
                    # logger.info(average)
                    place_score_avg_list.append(average)
                    
                    # diversity_score, geo_efficiency, place_score_avg, popular_dev 기반 강화학습 예정
                
            except Exception as e:
                logger.error("place_score_avg_list")
                logger.error(e)
                
            # 에러나서 안들어갈 경우 대비
            if len_place_score_avg_list == len(place_score_avg_list):
                place_score_avg_list.append(0)                

            if len(result) > 0:
                path_list.append(result)
                clustering_ok_list.append(clustering_ok)
        except Exception as error:
            logger.error(f"코스를 만드는 중에 에러 발생 :, {error}")
            logger.error(traceback.format_exc())
        
        
    # 클러스터링 잘 된 코스가 하나라도 있으면 안된 코스들은 제거
    if clustering_ok_list.count(True) > 1:
        len_path_list = len(path_list)
        new_path_list = []
        new_place_score_avg_list = []
        #path_list = [path for idx, path in enumerate(path_list) if clustering_ok_list[idx]]
        for idx, ok in enumerate(clustering_ok_list):
            if ok:
                new_path_list.append(path_list[idx])
                new_place_score_avg_list.append(place_score_avg_list[idx])
        
        path_list = copy.deepcopy(new_path_list)
        place_score_avg_list = new_place_score_avg_list

        logger.info(f"클러스터링 잘 안된 코스들은 제거, 갯수 : {len_path_list - len(path_list)}")

    
        # 교차하는 지점이 있는 코스 제거
        try:
            path_list_without_intersections, new_place_score_avg_list = copy.deepcopy(remove_routes_with_intersections(path_list, place_score_avg_list))
            
            path_list = copy.deepcopy(path_list_without_intersections)
            place_score_avg_list = new_place_score_avg_list
        except Exception as e:
            logger.error("교차 제거 중 에러 발생")
            logger.error(e)
    
    # 해시를 사용하여 중복 제거
    result = []
    seen_hashes = set()
    new_place_score_avg_list = []

    for idx, path in enumerate(path_list):
        a = copy.deepcopy(path)
        
        # 각 하루치 경로를 위도(lat) 기준으로 정렬
        sorted_a = [sorted(day, key=lambda place: place['lat']) for day in a]
        
        # 경로의 고유성을 해시값으로 표현하여 확인
        a_hash = tuple(hash_day(day) for day in sorted_a)
        
        # 고유한 해시값이 없는 경우만 결과에 추가
        if a_hash not in seen_hashes:
            seen_hashes.add(a_hash)
            result.append(copy.deepcopy(a))
            new_place_score_avg_list.append(place_score_avg_list[idx])
        else:
            logger.info(f"중복 제거 : {idx}번째 코스")
    place_score_avg_list = copy.deepcopy(new_place_score_avg_list)
    
            
    geo_score_list = []
    div_score = 0.0
    popular_scores_list = []
    
    result_eval = {}
    
    result_copy = copy.deepcopy(result)
    
    try:
        for idx, path in enumerate(result):
            
            geo_score_list.append(geo_efficiency(copy.deepcopy(path), place_score_avg_list[idx]))
            popular_scores_list.append(popularity_stats(copy.deepcopy(path)))
        div_score = diversity_score(copy.deepcopy(path_list))
            
        # logger.info("평가 함수")
        # logger.info(place_score_avg_list)
        # logger.info(geo_score_list)
        # logger.info(div_score)
        # logger.info(popular_scores_list)
        
            
        # 0~1 스케일로 정규화
        place_score_avg_list_norm = normalize_scores(place_score_avg_list)
        place_score_avg_list = copy.deepcopy(place_score_avg_list_norm)

        geo_score_list_norm = normalize_scores(geo_score_list)
        geo_score_list = copy.deepcopy(geo_score_list_norm)
                
            
        result_eval = {
            "place_score_avg_list":place_score_avg_list,
            "geo_score_list":geo_score_list,
            "diversity_score":div_score,
            "popular_scores_list":popular_scores_list,            
        }
        
                
        # place_score_avg_list와 result를 함께 (점수 기준) 내림차순 정렬
        combined = list(zip(place_score_avg_list, result))

        # 점수 내림차순 정렬
        combined_sorted = sorted(combined, key=lambda x: x[0], reverse=True)

        # 분리하면서 깊은 복사 수행
        #place_score_avg_list_sorted = [copy.deepcopy(item[0]) for item in combined_sorted]
        result_sorted = [copy.deepcopy(item[1]) for item in combined_sorted]

        # 기존 리스트 대신 새 리스트로 교체 X - 저장은 소트 안해도 되게 - 시간 절약
        # place_score_avg_list = place_score_avg_list_sorted
        result = copy.deepcopy(result_sorted)
        
        # 강화학습
        best_params = optimize_weights(result_eval)
        logger.info("best_params")
        logger.info(best_params)
            
    except Exception as e:
        logger.error("평가 함수 중 에러 발생")
        logger.error(traceback.format_exc())
        geo_score_list = []
        div_score = 0.0
        popular_scores_list = []
        result_eval = {}
        result = copy.deepcopy(result_copy)       
        
        
    # 최종 결과 결과 프린트 - 평시에는 주석 처리할 것
    # for idx_result, path_result in enumerate(result):
    #    logger.info(f"최종 코스 결과 , {idx_result}")
    #     for idx, day_path_result in enumerate(path_result):
    #        logger.info(f"{idx + 1},  일차 최종 코스 결과 ")
    #         for place_result in day_path_result:
    #            logger.info(place_result["name"])
    
    logger.info("최종 리턴하는 코스 수 : %s", str(len(result)))


    return result, enough_place, result_eval

def route_search_repeat(place_list, place_score_list, accomodation_list, essential_place_list, time_limit_list, params):
    n_day = params["n_day"]


    place_score_list_copy = copy.deepcopy(place_score_list)
    
    # 갔던 장소를 또 가지 않게 하기 위함
    place_score_list_not_in_path = copy.deepcopy(place_score_list)
    
    multi_day_path = []
    time_limit_final_list = []
    enough_time_list = []
    filtered_multi_day_path = []
    multi_day_place_idx_list = []
    
    # 날짜별 반복
    for i in range(n_day):

        #각 날짜별 시간 계산하는 부분 - 240123 보완
        time_limit = 540    #디폴트값
        if i == 0:
            time_limit = (18 - time_limit_list[0]) * 60
        elif i == n_day - 1:
            time_limit = (time_limit_list[1] - 11) * 60

        # 당일치기여행이면, time_limit_list[0]~time_limit_list[1]만 생각하면 된다.
        if n_day == 1:
            time_limit = time_limit_list[1] - time_limit_list[0]

            #당일치기라도, 점심 및 저녁 시간이 있으니, 제외하고 계산하기 위함
            time_limit = time_limit - 2 if time_limit > 6 else time_limit - 1

            time_limit = time_limit * 60
        
        # # 여유로운 여행이면, 60분 줄이기
        # if params["bandwidth"]:
        #     time_limit -= 60
            
        time_limit_final_list.append(time_limit)

        #각 날짜별 시간 계산하는 부분 종료

        result, enough_place, place_score_list_not_in_path, place_idx_list, enough_time = route_search_for_one_day(accomodation_list[i], accomodation_list[i + 1], place_list, place_score_list_copy, place_score_list_not_in_path, essential_place_list, time_limit, params, i)
        try:
            multi_day_place_idx_list += place_idx_list
        except Exception as e:
            logger.error("multi_day_place_idx_list")
            logger.error(e)

        # 각 날마다 장소 리스트를 깊은 복사: 각 날의 탐색은 독립적이어야 하므로, place_score_list_not_in_path를 각 날마다 깊은 복사해야 합니다.
        place_score_list_not_in_path_copy = copy.deepcopy(place_score_list_not_in_path)
        place_score_list_not_in_path = copy.deepcopy(place_score_list_not_in_path_copy)
        
        
        # 필터링: enough_time이 True인 경우만 필터링하여 `filtered_multi_day_path`에 추가
        if enough_time:
            filtered_multi_day_path.append(result)
        
        # 그리디 때문에 하루 path가 부족할 경우 클러스터링 쪽에서 문제 생겨서 추가 - TODO : 중간 날짜도 시간 조정이 가능해지면 로직 수정해야 함
        multi_day_path.append(copy.deepcopy(result))
        enough_time_list.append(enough_time)
        
        if not params["enough_place"]:
            if multi_day_path and len(multi_day_path[-1]) == 0:
                multi_day_path.pop()
                enough_time_list.pop()
            if filtered_multi_day_path and len(filtered_multi_day_path[-1]) == 0:
                filtered_multi_day_path.pop()
            break
        
    # 시간 제한이 너무 짧아 greedy 에서 관광지 추가 를 못한 경우 처리 - day_path 중 하나는 [] 또는 숙소만 있을 거임
    if not filtered_multi_day_path or not filtered_multi_day_path[0]:
        return [], [], False, False

        

    if len(filtered_multi_day_path) > 0:
        filtered_multi_day_path, clustering_ok = optimize_multi_day_path(filtered_multi_day_path, time_limit_final_list, params["move_time"], place_list, place_score_list_not_in_path)
    
    result_path = []
    index = 0
    
    # 나중에 모자란 배열을 같은 위치에 추가
    for i, enough_time in enumerate(enough_time_list):
        if enough_time:
            result_path.append(filtered_multi_day_path[index])
            index += 1
        else:
            result_path.append(multi_day_path[i])
    
    return result_path, multi_day_place_idx_list, enough_place, clustering_ok

def route_search_for_one_day(accomodation1, accomodation2, place_list, place_score_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day):
    transit = params["transit"]
    
    # 남은 관광지가 없을 경우 바로 리턴
    if len(place_score_list_not_in_path) <= 0:
        logger.info(f"관광지가 부족할 경우 (2) / 관광지 갯수 : {len(place_score_list)}")

        params["enough_place"] = False
        return [], params["enough_place"], place_score_list_not_in_path, [], False
    
    # 코스 초안을 만드는 그리디 알고리즘 부분
    path, time_coast, score_sum, place_idx_list, enough_place = initialize_greedy(accomodation1, place_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day)
            
    # 그리디 결과 프린트 - 평시에는 주석 처리할 것
    # print(params["repeat_count"], " 번째 그리디 결과")
    # for place in path:
    #     print(place["name"])
        
    if not accomodation2["is_dummy"]:
        path.append(accomodation2)
        time_coast += 30            # 숙소는 더이상 소요시간 x. 숙소까지 이동하는 시간 추가
        
    
    # 남은 관광지가 없을 경우 힐클라이밍 건너뛰고 tsp만하고 리턴
    if len(place_score_list_not_in_path) <= 0:
        path, _ = tsp(path)
        return path, params["enough_place"], place_score_list_not_in_path, place_idx_list, False
        
    
    # 시간 제한이 너무 짧아 greedy 에서 관광지 추가를 못한 경우 - 바로 리턴 -> path = []
    elif len(place_idx_list) == 0:
        logger.info("시간 제한이 너무 짧아 greedy 에서 관광지 추가를 못한 경우 - 바로 리턴")
        return path, enough_place, place_score_list_not_in_path, place_idx_list, False
        
        
    path, idx_list, enough_place = copy.deepcopy(hill_climb(place_list, place_score_list_not_in_path, place_idx_list, path, params))
    
    # 힐 클라이밍 이후 시간 제한 이상으로 튀어버린 여행 코스 뒷부분부터 pop - TODO 어차피 전체 경로 최적화 후에 이 작업 한 번 더 하니까, 하단 TODO 해결될 때 까진 주석
    # moving_transit = CAR_TRANSIT if transit == 0 else PUBLIC_TRANSIT
    # #moving_time = (len(path) - 1) * moving_transit
    # popper = len(path)
    
    # # "is_accomodation" 값이 False인 장소들의 개수를 계산 - 아래 반복문에서 
    # non_accommodation_count = sum(1 for place in path if not place["is_accomodation"])
    
    # while time_coast > time_limit + OVER_TIME and popper > 0 and non_accommodation_count > 1:
    #     popper -= 1
    #     if not path[popper]["is_essential"]:
    #         place = path.pop(popper)
    #         idx = place_idx_list.pop()
    #         #moving_time = (len(path) - 1) * moving_transit
    #         score_sum -= idx[0]
    #         time_coast -= place["takenTime"]
    #         time_coast -= params["move_time"]
    #         non_accommodation_count -= 1
            
    #         # 관광지 점수 리스트도 업데이트 - 만약 같은 관광지 중복으로 뜨는 문제 생기면 여기 지울 것! - TODO 중복 문제 해결하고 이거 주석 풀 것
    #         #place_score_list_not_in_path.append(copy.deepcopy([idx[0],idx[1],idx[2]]))
    #         #place_score_list_not_in_path.sort(key=lambda x: x[0])

    return path, enough_place, place_score_list_not_in_path, place_idx_list, True