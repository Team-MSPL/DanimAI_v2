import copy
from .distance import tsp
from .cluster import cluster_with_hdbscan
from ..logging_config import logger
from ..common.constant import OVER_TIME, UNDER_TIME
import random
import numpy as np
from scipy.spatial.distance import cdist

def is_within_range(place1, place2, target_place):
    lat_min = min(place1['lat'], place2['lat'])
    lat_max = max(place1['lat'], place2['lat'])
    lng_min = min(place1['lng'], place2['lng'])
    lng_max = max(place1['lng'], place2['lng'])

    is_lat_within = lat_min <= target_place['lat'] <= lat_max
    is_lng_within = lng_min <= target_place['lng'] <= lng_max

    return is_lat_within and is_lng_within

def check_enough_place(day_path, day_idx, move_time, time_limit_list, len_place_score_list_not_in_path):
    total_time = sum(place["takenTime"] for place in day_path)
    total_time += move_time * (len(day_path) - 1)
    if total_time >= time_limit_list[day_idx] - UNDER_TIME or len_place_score_list_not_in_path == 0:
        return True
    else:
        return False

def fill_time_loss(day_idx, day_path, final_optimized_path, time_limit_list, move_time, place_list, place_score_list_not_in_path):
    try:
        # 당일치기인 경우
        if len(time_limit_list) == 1:
            # 당일치기 + 관광지 2개 이상
            if len(day_path) >= 2:
                place1 = {"lat":day_path[0]["lat"], "lng":day_path[0]["lng"]}
                place2 = {"lat":day_path[-1]["lat"], "lng":day_path[-1]["lng"]}
                
                popper = len(place_score_list_not_in_path) - 1
                for i in range(len(place_score_list_not_in_path)):
                    score_idx_name = place_score_list_not_in_path[popper]
                    search_place = place_list[score_idx_name[1]]
                    
                    if is_within_range(place1,place2,search_place):
                        
                        add_place = copy.deepcopy(search_place)
                        
                        day_path.insert(-1, add_place)
                        
                        del place_score_list_not_in_path[popper]
                        
                        logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - 당일치기 - %s", add_place["name"])
                        
                        if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                            return day_path
                        
                    popper -= 1
                
            # 당일치기 + 관광지 1개 이하 + 2개 이상인데, 위에서 충분히 못 채운 경우
            #central_point = {"lat":day_path[0]["lat"], "lng":day_path[0]["lng"]}
            # 중간값 계산
            median_index = len(place_score_list_not_in_path) // 2
            total_time = sum(place["takenTime"] for place in day_path)
            total_time += move_time * (len(day_path) - 1)
                
            for index, score_index_name in enumerate(place_score_list_not_in_path):
                if index >= median_index and place_list[score_index_name[1]]["takenTime"] <= total_time - (time_limit_list[day_idx] - UNDER_TIME):
                    
                    add_place = copy.deepcopy(place_list[score_index_name[1]])
                    
                    day_path.append(add_place)
                        
                    del place_score_list_not_in_path[index]
                        
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - 당일치기 2 - %s", add_place["name"])
                        
                    if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                        return day_path
            
        # 1박 2일 이상
        else:
            # 위도와 경도를 범위로 동선 안해치는 관광지를 추가 ( 점수 높은 순서대로 고려 )
            # 마지막날이 아니면 다음날 첫 여행지를 기준으로
            if day_idx != len(final_optimized_path) - 1:
                place1 = {"lat":day_path[-1]["lat"], "lng":day_path[-1]["lng"]}
                place2 = {"lat":final_optimized_path[day_idx + 1][0]["lat"], "lng":final_optimized_path[day_idx + 1][0]["lng"]}
                # 이날 마지막 여행지가 숙소라면 숙소와의 비교
                if day_path[-1]["is_accomodation"]:
                    place2 = {"lat":day_path[-2]["lat"], "lng":day_path[-2]["lng"]}
                
                popper = len(place_score_list_not_in_path) - 1
                for i in range(len(place_score_list_not_in_path)):
                    score_idx_name = place_score_list_not_in_path[popper]
                    search_place = place_list[score_idx_name[1]]
                    
                    if is_within_range(place1,place2,search_place):
                        
                        add_place = copy.deepcopy(search_place)
                        
                        if day_path[-1]["is_accomodation"]:
                            day_path.insert(-1, add_place)
                        else:
                            day_path.append(add_place)
                        
                        del place_score_list_not_in_path[popper]
                        
                        logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - %s", add_place["name"])
                        
                        if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                            return day_path
                        
                    popper -= 1
                    
            # 첫날이 아니면 전날 마지막 여행지를 기준으로
            if day_idx != 0:
                place1 = {"lat":day_path[0]["lat"], "lng":day_path[0]["lng"]}          
                place2 = {"lat":final_optimized_path[day_idx-1][-1]["lat"], "lng":final_optimized_path[day_idx-1][-1]["lng"]}
                # 이날 첫 여행지가 숙소라면, 숙소와 비교
                if day_path[0]["is_accomodation"] and len(day_path) > 1:
                    place2 = {"lat":day_path[1]["lat"], "lng":day_path[1]["lng"]}    
                
                popper = len(place_score_list_not_in_path) - 1
                for i in range(len(place_score_list_not_in_path)):
                    score_idx_name = place_score_list_not_in_path[popper]
                    search_place = place_list[score_idx_name[1]]
                    
                    if is_within_range(place1,place2,search_place):
                        
                        add_place = copy.deepcopy(search_place)
                        
                        if day_path[0]["is_accomodation"]:
                            day_path.insert(1, add_place)
                        else:
                            day_path.insert(0, add_place)
                            
                        del place_score_list_not_in_path[popper]
                        
                        logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v2 - %s", add_place["name"])
                        
                        if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                            return day_path
                        
                    popper -= 1
                    
            
            # 위도와 경도 범위 안에 아무것도 없을 경우 - 이후로는 중점 좌표 기준으로 채우기
            # 거리가 가까운 순으로 보되 ( place1, place2 사이의 거리보다는 짧아야함. - 원 범위 ), 점수가 남은 장소 점수들의 중간값보다는 높아야 함
            # 마지막날이 아니면 다음날 첫 여행지를 기준으로
            if day_idx != len(final_optimized_path) - 1:
                place1 = {"lat":day_path[-1]["lat"], "lng":day_path[-1]["lng"]}
                place2 = {"lat":final_optimized_path[day_idx + 1][0]["lat"], "lng":final_optimized_path[day_idx + 1][0]["lng"]}
                # 이날 마지막 여행지가 숙소라면 숙소와의 비교
                if day_path[-1]["is_accomodation"]:
                    place2 = {"lat":day_path[-2]["lat"], "lng":day_path[-2]["lng"]}
                    
                central_point = {"lat":(place1["lat"] + place2["lat"]) / 2, "lng":(place1["lng"] + place2["lng"]) / 2}
                
                # 중간값 계산
                median_index = len(place_score_list_not_in_path) // 2
            
                # place1과 place2 사이의 거리 계산
                max_distance_square = (place1["lat"] - place2["lat"])**2 + (place1["lng"] - place2["lng"])**2
                
                # 중간값 이상의 장소 필터링
                filtered_places = []
                for score, index, name in place_score_list_not_in_path:
                    if index >= median_index:
                        place = place_list[index]
                        distance_to_central_square = (central_point["lat"] - place["lat"])**2 + (central_point["lng"] - place["lng"])**2
                        
                        # 중앙점과의 거리가 place1, place2 사이 거리보다 짧을 때만 추가 - 이거보다 멀리 있으면 추가 안하는게 보기 더 좋을 듯
                        if distance_to_central_square <= max_distance_square:
                            filtered_places.append((distance_to_central_square, place))
            
                # 거리 기준으로 정렬
                closest_places = sorted(filtered_places, key=lambda x: x[0])
                closest_places = [place for _, place in closest_places]
                
                for item in closest_places:
                    
                    add_place = copy.deepcopy(item)
                    
                    if day_path[-1]["is_accomodation"]:
                        day_path.insert(-1, add_place)
                    else:
                        day_path.append(add_place)
                    
                    place_score_list_not_in_path = [element for element in place_score_list_not_in_path if element[2] != add_place["name"]]
                    
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v3 - %s", add_place["name"])
                    
                    if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                        return day_path
            
            
            # 첫날이 아니면 전날 마지막 여행지를 기준으로
            if day_idx != 0:
                place1 = {"lat":day_path[0]["lat"], "lng":day_path[0]["lng"]}          
                place2 = {"lat":final_optimized_path[day_idx-1][-1]["lat"], "lng":final_optimized_path[day_idx-1][-1]["lng"]}
                # 이날 첫 여행지가 숙소라면, 숙소와 비교
                if day_path[0]["is_accomodation"]:
                    place2 = {"lat":day_path[1]["lat"], "lng":day_path[1]["lng"]} 
                    
                central_point = {"lat":(place1["lat"] + place2["lat"]) / 2, "lng":(place1["lng"] + place2["lng"]) / 2}
                
                # 중간값 계산
                median_index = len(place_score_list_not_in_path) // 2
            
                # place1과 place2 사이의 거리 계산
                max_distance_square = (place1["lat"] - place2["lat"])**2 + (place1["lng"] - place2["lng"])**2
                
                # 중간값 이상의 장소 필터링
                filtered_places = []
                for score, index, name in place_score_list_not_in_path:
                    if index >= median_index:
                        place = place_list[index]
                        distance_to_central_square = (central_point["lat"] - place["lat"])**2 + (central_point["lng"] - place["lng"])**2
                        
                        # 중앙점과의 거리가 place1, place2 사이 거리보다 짧을 때만 추가 - 이거보다 멀리 있으면 추가 안하는게 보기 더 좋을 듯
                        if distance_to_central_square <= max_distance_square:
                            filtered_places.append((distance_to_central_square, place))
            
                # 거리 기준으로 정렬
                closest_places = sorted(filtered_places, key=lambda x: x[0])
                closest_places = [place for _, place in closest_places]
                
                for item in closest_places:
                    
                    add_place = copy.deepcopy(item)
                    
                    if day_path[0]["is_accomodation"]:
                        day_path.insert(1, add_place)
                    else:
                        day_path.insert(0, add_place)
                        
                    place_score_list_not_in_path = [element for element in place_score_list_not_in_path if element[2] != add_place["name"]]
                    
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v4 - %s", add_place["name"])
                    
                    if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                        return day_path
    except Exception as error:
        logger.error(f"fill_time_loss 중에 에러 발생 :, {error}")  
    return day_path

    
        # # 만약 갯수가 부족할 경우 - 중간값 하, 0 이상의 장소도 필터링
        # filtered_places = []
        # for score, index, name in place_score_list_not_in_path:
        #     if index >= median_index:
        #         place = place_list[index]
        #         distance_to_central_square = (central_point["lat"] - place["lat"])**2 + (central_point["lng"] - place["lng"])**2
                
        #         # 중앙점과의 거리가 place1, place2 사이 거리보다 짧을 때만 추가 - 이거보다 멀리 있으면 추가 안하는게 보기 더 좋을 듯
        #         if distance_to_central_square <= max_distance_square:
        #             filtered_places.append((distance_to_central_square, place))

def optimize_multi_day_path(multi_day_path, time_limit_list, move_time, place_list, place_score_list_not_in_path):    
    places_to_cluster = []
    
    essential_count_list = [0 for i in range(len(multi_day_path))]
    day_path_list_with_essential = []
    
    # Step 1: 숙소, 필수여행지를 뺀 관광지들을 전부 추출
    for idx, day_path in enumerate(multi_day_path):
        for place in day_path:
            if not place["is_essential"]:
                places_to_cluster.append(copy.deepcopy(place))
            else:
                if not place["is_accomodation"]:
                    essential_count_list[idx] += 1
                    
    
    #하루당 평균 관광지 수 - places_to_cluster 갯수에 따라 변하지 않도록
    len_places_to_cluster = len(places_to_cluster) 
    place_num_avg = len_places_to_cluster // len(multi_day_path)
    all_place_num_avg = (len_places_to_cluster + sum(essential_count_list)) // len(multi_day_path)
    
    # 전부 필수여행지로만 채운 경우, 바로 리턴
    if len(places_to_cluster) < 2 or place_num_avg < 2:
        logger.info(f"여행지 갯수가 거의 없는 경우 - 바로 리턴, place_num_avg :  {place_num_avg}, len_places_to_cluster : {len_places_to_cluster}")
        final_optimized_path = []
        for i, day_path in enumerate(multi_day_path):
            optimized_day_path, _ = tsp(day_path)
            final_optimized_path.append(copy.deepcopy(optimized_day_path))
        return final_optimized_path, False
    
    # 소숫점 첫째자리가 5이상이면 +2, 아니면 +1
    max_cluster_size = place_num_avg + 2 if int(len(places_to_cluster) / len(multi_day_path) * 10) % 10 >= 5 else place_num_avg + 1
    
    
    # Step 2: 필수 여행지가 있는 경우 당일 배정된 필수 여행지들의 중점 좌표와 가까운 장소들로 채워서, 갯수가 all_place_num_avg 이상이 되게 
    for day_idx, day_path in enumerate(multi_day_path):
        if essential_count_list[day_idx] > 0:
            essential_places = [place for place in day_path if place["is_essential"]]
            essential_places_without_accomodation = [place for place in day_path if place["is_essential"] and not place["is_accomodation"]]
            
            
            total_time = sum(place["takenTime"] for place in essential_places_without_accomodation)
            total_time += move_time * (len(essential_places) - 1)        
            
            # 필수 여행지 ( + 있다면 숙소도 ) 의 평균 좌표 계산
            essential_coordinates = np.array([[place['lat'], place['lng']] for place in essential_places])
            essential_center = np.mean(essential_coordinates, axis=0)

            places_to_add = []            
            if len(places_to_cluster) > 0:
                # places_to_cluster 내 장소들과의 거리 계산
                distances = cdist([essential_center], [[place['lat'], place['lng']] for place in places_to_cluster])
                
                # 가까운 장소부터 all_place_num_avg 수 만큼 추가
                sorted_indices = np.argsort(distances[0])
                
                for i in sorted_indices[:all_place_num_avg - len(essential_places_without_accomodation)]:
                    places_to_add.append(copy.deepcopy(places_to_cluster[i]))
                    
                    total_time += places_to_cluster[i]["takenTime"] + move_time
                    if not total_time < time_limit_list[day_idx] - UNDER_TIME:
                        break
                
                for i, item in enumerate(places_to_add):
                    # 추가한 장소는 places_to_cluster에서 제거
                    if item in places_to_cluster:
                        places_to_cluster.remove(item)
                    
            # 하루치 코스 구성
            new_day_path = []
            
            if day_path[0]["is_accomodation"]:
                new_day_path.append(copy.deepcopy(day_path[0]))
            
            new_day_path.extend(copy.deepcopy(essential_places_without_accomodation))
            new_day_path.extend(copy.deepcopy(places_to_add))
            
            if day_path[-1]["is_accomodation"]:
                new_day_path.append(copy.deepcopy(day_path[-1]))
            
            optimized_new_day_path, _ = tsp(new_day_path)
            
            day_path_list_with_essential.append(optimized_new_day_path)
        else:
            day_path_list_with_essential.append([]) # index 맞추기
            
    
    # Step 3: 클러스터링 - 인접한 관광지끼리 묶음. min_cluster_size는 하루당 평균 관광지 수를 기반으로
    clustering_ok = False
    clustered_places = []
    
    len_places_to_cluster2 = len(places_to_cluster) 
    essential_count_list_count_zero = essential_count_list.count(0) 
    
    if essential_count_list.count(0) > 0:
        clustered_places, clustering_ok = cluster_with_hdbscan(places_to_cluster, essential_count_list.count(0), all_place_num_avg, max_cluster_size)
        
    clustered_places_copy = copy.deepcopy(clustered_places)

    final_optimized_path = []
    
    # Step 4 : 코스 최적화
    for idx, day_path in enumerate(multi_day_path):        
        # 필수여행지가 포함된 날이면, Step 2에서 따로 만든 코스를 사용
        if essential_count_list[idx] > 0:
            final_optimized_path.append(copy.deepcopy(day_path_list_with_essential[idx]))
        else:
            new_day_path = []
            if day_path[0]["is_accomodation"]:
                new_day_path.append(copy.deepcopy(day_path[0]))
                
            #클러스터를 new_day_path에 추가
            add_place_list = copy.deepcopy(clustered_places.pop(0))
            
            # 예외 처리 - 그대로 리턴 - clustered_places에 []가 섞인 경우
            if add_place_list is None or len(add_place_list) == 0:
                logger.error("clustered_places_copy")
                logger.error(clustered_places_copy)
                logger.error("len_places_to_cluster")
                logger.error(len_places_to_cluster)
                logger.error("len_places_to_cluster2")
                logger.error(len_places_to_cluster2)
                logger.error("place_num_avg")
                logger.error(place_num_avg)
                logger.error("essential_count_list_count_zero")
                logger.error(essential_count_list_count_zero)
                return multi_day_path, False
            
            new_day_path.extend(add_place_list)
                        
            if day_path[-1]["is_accomodation"]:
                new_day_path.append(copy.deepcopy(day_path[-1]))
                
            if len(new_day_path) > 0:
                optimized_new_day_path, _ = tsp(new_day_path)
            else:
                optimized_new_day_path = new_day_path
            
            final_optimized_path.append(optimized_new_day_path)
        
        
    # Step 5: 시간 초과, 부족 시 경로 수정
    for day_idx, day_path in enumerate(final_optimized_path):
        total_time = sum(place["takenTime"] for place in day_path)
        total_time += move_time * (len(day_path) - 1)
        
        # "is_accomodation" 값이 False인 장소들의 개수를 계산
        non_accommodation_count = sum(1 for place in day_path if not place["is_accomodation"])
                
        # 시간 초과 발생 시 처리 -  여유를 줌 + 하루에 관광지가 하나인 경우는 빼고 ( 하루 종일 )
        if total_time > time_limit_list[day_idx] + OVER_TIME and non_accommodation_count > 1:
            #logger.info(f"Day {day_idx+1}의 시간 제한 + OVER_TIME 초과: {total_time} > {time_limit_list[day_idx] + OVER_TIME}")
            
            non_essential_places = [place for place in day_path if not place["is_essential"] and not place["is_accomodation"]]
            
            # 랜덤하게 비필수 장소 제거 ( 기준 변경 가능 ) + day_path가 최소 1개는 남아야 함
            # 숙소 하나만 남는 경우 제외하기
            while non_essential_places and total_time > time_limit_list[day_idx] + OVER_TIME and len(day_path) > 1 and non_accommodation_count > 1:
                place_to_remove = random.choice(non_essential_places)  # 랜덤 선택
                non_essential_places.remove(place_to_remove)  # 목록에서 제거
                day_path.remove(place_to_remove)  # 경로에서 제거
                total_time -= place_to_remove["takenTime"]
                total_time -= move_time  # 장소 하나 제거했으므로 이동 시간도 감소
                non_accommodation_count = sum(1 for place in day_path if not place["is_accomodation"])
                
                #  TODO place_list에서 찾아서 place_score_list_not_in_path에 다시 추가
                
            # 최적화 후에도 시간 초과가 계속되면 원래 경로 복구 - 그리디에서 무조건 하나는 주게 수정하였기에, 이것도 수정 - TODO 변경 필요
            # if total_time > time_limit_list[day_idx] + OVER_TIME:
            #     logger.info(f"전체 경로 최적화 후 시간 제한 초과하여, Day {day_idx+1} 경로 원래대로 복구")
            #     return multi_day_path, clustering_ok
            
            
        # 시간 부족 발생 시 처리 (초과 처리 이후 확인 - 부족보단 많은게 낫다고 판단)
        if total_time < time_limit_list[day_idx] - UNDER_TIME:
            #logger.info(f"Day {day_idx+1}의 시간 제한 - UNDER_TIME 미만: {total_time} < {time_limit_list[day_idx] - UNDER_TIME}")

            day_path = fill_time_loss(
                day_idx, day_path, final_optimized_path, 
                time_limit_list, move_time, 
                place_list, place_score_list_not_in_path
            )

    
    return final_optimized_path, clustering_ok