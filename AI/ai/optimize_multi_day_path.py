import copy
from .distance import tsp

def optimize_multi_day_path(multi_day_path, time_limit_list, move_time):
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
            
            # 숙소 or 필수 여행지도 각각의 세그먼트에 넣어야 하니까 + 4시간 이상의 긴 관광지는 위치가 바뀌면 전체 경로가 꼬이는 경우가 많음 TODO 빼도 되는지 테스트
            if place["is_essential"] or place["takenTime"] >= 240:
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
    
    
    # # Step 4: 만약 코스별 제한 시간이 많이 초과될 경우, 원래 코스 리턴
    # for day_idx, day_path in enumerate(final_optimized_path):
    #     total_time = sum(place["takenTime"] for place in day_path)
    #     total_time += move_time * (len(day_path) - 1)
        
    #     # "is_accomodation" 값이 False인 장소들의 개수를 계산
    #     non_accommodation_count = sum(1 for place in day_path if not place["is_accomodation"])

        
    #     # 시간 제한 초과 시, 원래 경로로 대체 - 30분 여유를 줌 + 하루에 관광지가 하나인 경우는 빼고 ( 하루 종일 )
    #     if total_time > time_limit_list[day_idx] + 30 and non_accommodation_count > 1:
    #         print("전체 경로 최적화 후 시간 제한 초과하여, 전체 경로 최적화 작업물 복구")
    #         print(total_time)
    #         print(time_limit_list[day_idx])
    #         return multi_day_path
        

    # Step 4: 시간 초과 시 경로 수정
    for day_idx, day_path in enumerate(final_optimized_path):
        total_time = sum(place["takenTime"] for place in day_path)
        total_time += move_time * (len(day_path) - 1)
        
        # "is_accomodation" 값이 False인 장소들의 개수를 계산
        non_accommodation_count = sum(1 for place in day_path if not place["is_accomodation"])
        
        # 시간 초과 발생 시 처리 - 30분 여유를 줌 + 하루에 관광지가 하나인 경우는 빼고 ( 하루 종일 )
        if total_time > time_limit_list[day_idx] + 30 and non_accommodation_count > 1:
            print(f"Day {day_idx+1}의 시간 제한 초과: {total_time} > {time_limit_list[day_idx]}")

            # 비필수 장소 목록 필터링
            non_essential_places = [place for place in day_path if not place["is_essential"] and not place["is_accomodation"]]

            # 인기도가 낮은 비필수 장소 순으로 정렬 ( 기준 변경 가능 )
            non_essential_places.sort(key=lambda place: place["popular"], reverse=False)
            
            # 시간 초과를 해결할 때까지 비필수 장소 제거
            while non_essential_places and total_time > time_limit_list[day_idx] + 30:
                place_to_remove = non_essential_places.pop(0)
                day_path.remove(place_to_remove)
                total_time -= place_to_remove["takenTime"]
                total_time -= move_time  # 장소 하나 제거했으므로 이동 시간도 감소
                
                print(f"Removed {place_to_remove['name']} to reduce time. New total time: {total_time}")
            
            # 최적화 후에도 시간 초과가 계속되면 원래 경로 복구
            if total_time > time_limit_list[day_idx] + 30:
                print(f"전체 경로 최적화 후 시간 제한 초과하여, Day {day_idx+1} 경로 원래대로 복구")
                return multi_day_path
            
    return final_optimized_path