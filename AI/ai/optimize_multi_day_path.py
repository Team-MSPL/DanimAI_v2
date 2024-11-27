import copy
from .distance import tsp
from ..logging_config import logger
from ..common.constant import OVER_TIME, UNDER_TIME
import random

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
                    
                    day_path.insert(-1, copy.deepcopy(search_place))
                    
                    del place_score_list_not_in_path[popper]
                    
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - %s", search_place["name"])
                    
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
            if score_index_name[1] >= median_index and place_list[score_index_name[1]]["takenTime"] <= total_time - (time_limit_list[day_idx] - UNDER_TIME):
                day_path.append(copy.deepcopy(place_list[index]))
                    
                del place_score_list_not_in_path[index]
                    
                logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - %s", place_list[index]["name"])
                    
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
                    if day_path[-1]["is_accomodation"]:
                        day_path.insert(-1, copy.deepcopy(search_place))
                    else:
                        day_path.append(copy.deepcopy(search_place))
                    
                    del place_score_list_not_in_path[popper]
                    
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 - %s", search_place["name"])
                    
                    if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                        return day_path
                    
                popper -= 1
                
        # 첫날이 아니면 전날 마지막 여행지를 기준으로
        if day_idx != 0:
            place1 = {"lat":day_path[0]["lat"], "lng":day_path[0]["lng"]}          
            place2 = {"lat":final_optimized_path[day_idx-1][-1]["lat"], "lng":final_optimized_path[day_idx-1][-1]["lng"]}
            # 이날 첫 여행지가 숙소라면, 숙소와 비교
            if day_path[0]["is_accomodation"]:
                place2 = {"lat":day_path[1]["lat"], "lng":day_path[1]["lng"]}    
            
            popper = len(place_score_list_not_in_path) - 1
            for i in range(len(place_score_list_not_in_path)):
                score_idx_name = place_score_list_not_in_path[popper]
                search_place = place_list[score_idx_name[1]]
                
                if is_within_range(place1,place2,search_place):
                    if day_path[0]["is_accomodation"]:
                        day_path.insert(1, copy.deepcopy(search_place))
                    else:
                        day_path.insert(0, copy.deepcopy(search_place))
                        
                    del place_score_list_not_in_path[popper]
                    
                    logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v2 - %s", search_place["name"])
                    
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
                if day_path[-1]["is_accomodation"]:
                    day_path.insert(-1, copy.deepcopy(item))
                else:
                    day_path.append(copy.deepcopy(item))
                
                del place_score_list_not_in_path[popper]
                
                logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v3 - %s", item["name"])
                
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
                if day_path[0]["is_accomodation"]:
                    day_path.insert(1, copy.deepcopy(item))
                else:
                    day_path.insert(0, copy.deepcopy(item))
                    
                del place_score_list_not_in_path[popper]
                
                logger.info("전체 경로 최적화 후 시간 제한 미달하여 관광지 추가 v4 - %s", item["name"])
                
                if check_enough_place(day_path, day_idx, move_time, time_limit_list, len(place_score_list_not_in_path)):
                    return day_path
                    
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
    path_segment = []
    path_segment_list = []
    optimized_segment_list = []
    place_num_per_day = []
    
    # Step 1: 숙소 or 필수 여행지를 기준으로 전체 코스를 세그먼트로 분할
    for day_path in multi_day_path:
        # 나중에, 원래 하루에 장소가 몇 개씩 있었는지 알게 하기 위함
        place_num_per_day.append(len(day_path))
        
        for place in day_path:
            
            path_segment.append(copy.deepcopy(place))
            
            # 숙소 or 필수 여행지도 각각의 세그먼트에 넣어야 하니까
            # 4시간 이상의 긴 관광지는 위치가 바뀌면 전체 경로가 꼬이는 경우가 많음 TODO 빼도 되는지 테스트
            #if place["is_essential"] or place["takenTime"] >= 240:
            if place["is_essential"]:
                path_segment_list.append(copy.deepcopy(path_segment))
                
                new_path_segment = [copy.deepcopy(place)]  # 숙소 or 필수 여행지로 시작하는 새로운 세그먼트 - [숙소, 숙소] 세그먼트가 발생하기는 함
                path_segment = copy.deepcopy(new_path_segment)
                
    # 마지막 세그먼트까지 추가
    path_segment_list.append(copy.deepcopy(path_segment))

    # Step 2: 각각의 세그먼트를 대상으로 tsp 실행
    for segment in path_segment_list:
        optimized_segment, _ = tsp(segment)
        optimized_segment_list.append(optimized_segment)
    
    # Step 3: 각각의 세그먼트를 다시 path로 쪼개 넣어 줌
    #for segment_idx, segment in enumerate(optimized_segment_list):
    #   for place_idx, place in enumerate(segment):
    
    final_optimized_path = []
    segment_index = 0

    for num_places in place_num_per_day:
        day_path = []

        # 현재 날짜의 세그먼트가 끝나는 위치
        places_needed = num_places
        while places_needed > 0:
            segment = optimized_segment_list[segment_index]
            
            # 현재 세그먼트에서 가능한 장소를 추가
            while places_needed > 0 and segment:
                day_path.append(segment.pop(0))
                places_needed -= 1

            # 다음 세그먼트로 넘어가기
            if not segment:
                segment_index += 1
                
                if segment_index >= len(optimized_segment_list):
                    break
                
                # 세그먼트의 첫 원소는 이전 세그먼트의 마지막 원소와 중복이므로 pop
                optimized_segment_list[segment_index].pop(0)
        
        final_optimized_path.append(day_path)
    
    # Step 4: 시간 초과 시 경로 수정
    for day_idx, day_path in enumerate(final_optimized_path):
        total_time = sum(place["takenTime"] for place in day_path)
        total_time += move_time * (len(day_path) - 1)
        
        # "is_accomodation" 값이 False인 장소들의 개수를 계산
        non_accommodation_count = sum(1 for place in day_path if not place["is_accomodation"])
                
        # 시간 초과 발생 시 처리 -  여유를 줌 + 하루에 관광지가 하나인 경우는 빼고 ( 하루 종일 )
        if total_time > time_limit_list[day_idx] + OVER_TIME and non_accommodation_count > 1:
            logger.info(f"Day {day_idx+1}의 시간 제한 + OVER_TIME 초과: {total_time} > {time_limit_list[day_idx] + OVER_TIME}")

            # 비필수 장소 목록 필터링
            non_essential_places = [place for place in day_path if not place["is_essential"] and not place["is_accomodation"]]

            # # 인기도가 낮은 비필수 장소 순으로 정렬 ( 기준 변경 가능 )
            # non_essential_places.sort(key=lambda place: place["popular"], reverse=False)
            
            # # 시간 초과를 해결할 때까지 비필수 장소 제거
            # while non_essential_places and total_time > time_limit_list[day_idx] + OVER_TIME:
            #     place_to_remove = non_essential_places.pop(0)
            #     day_path.remove(place_to_remove)
            #     total_time -= place_to_remove["takenTime"]
            #     total_time -= move_time  # 장소 하나 제거했으므로 이동 시간도 감소
                
            #     logger.info(f"Removed {place_to_remove['name']} to reduce time. New total time: {total_time}")
            
            # 랜덤하게 비필수 장소 제거 ( 기준 변경 가능 )
            while non_essential_places and total_time > time_limit_list[day_idx] + OVER_TIME:
                place_to_remove = random.choice(non_essential_places)  # 랜덤 선택
                non_essential_places.remove(place_to_remove)  # 목록에서 제거
                day_path.remove(place_to_remove)  # 경로에서 제거
                total_time -= place_to_remove["takenTime"]
                total_time -= move_time  # 장소 하나 제거했으므로 이동 시간도 감소
                
                logger.info(f"Removed {place_to_remove['name']} randomly to reduce time. New total time: {total_time}")

            
            # 최적화 후에도 시간 초과가 계속되면 원래 경로 복구
            if total_time > time_limit_list[day_idx] + OVER_TIME:
                logger.info(f"전체 경로 최적화 후 시간 제한 초과하여, Day {day_idx+1} 경로 원래대로 복구")
                return multi_day_path
            
            
        # 시간 부족 발생 시 처리 (초과 처리 이후 확인 - 부족보단 많은게 낫다고 판단)
        if total_time < time_limit_list[day_idx] - UNDER_TIME:
            logger.info(f"Day {day_idx+1}의 시간 제한 - UNDER_TIME 미만: {total_time} < {time_limit_list[day_idx] - UNDER_TIME}")

            day_path = fill_time_loss(
                day_idx, day_path, final_optimized_path, 
                time_limit_list, move_time, 
                place_list, place_score_list_not_in_path
            )
            logger.info(f"Time loss filled for Day {day_idx+1}. New total time: {total_time}")

    
    return final_optimized_path