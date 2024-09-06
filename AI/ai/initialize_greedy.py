


def initialize_greedy(accomodation1, place_list, place_list_not_in_path, place_score_list, place_score_list_not_in_path, essential_place_list, time_limit, params, day):
    path = []
    time_coast = 0
    score_sum = 0
    place_idx_list = []     # 관광지별 점수를 배열에 저장해 둠. 사실상 path의 score_list
    
    if not accomodation1["is_dummy"]:
        path.append(accomodation1)
        time_coast += accomodation1["takenTime"]
        # 이동시간 추가
        time_coast += params["move_time"]
    for essential in essential_place_list:
        
        # 필수 여행지의 day값이 현재 그리디 중인 path의 날짜와 같아야만 path에 넣음
        if not essential["is_dummy"] and essential["day"] == day + 1:
            path.append(essential)
            time_coast += essential["takenTime"]
            # 이동시간 추가
            time_coast += params["move_time"]
            
    # 그리디 부분에서는 거리 계산을 안하는거로 함 ( 변동 가능 ) TODO 거리 계산까지 넣어보고 결과 비교
    
    # repeat_count만큼 더 내려가서 반복마다 차이를 줌 
    popper = len(place_score_list_not_in_path) - 1 - params["repeat_count"]
    
    # 그리디 반복 부분 - place_score_list_not_in_path 사용
    while time_limit > time_coast and len(path) < 5 and popper >= 0:
        
        
        # 관광지가 부족할 경우 (1)
        if len(place_score_list_not_in_path) < 0:        
            print("관광지가 부족할 경우 (1) / 관광지 갯수 : ", len(place_score_list))
            params["enough_place"] = False
            break
        
        
        place_idx = place_score_list_not_in_path[popper]
        popper -= 1
        
        # 너무 모자라도 안되니까 30분 여유를 줌 ( 원 코드 204줄 )
        if place_list_not_in_path[place_idx[1]] is not None:
            
            place = place_list_not_in_path[place_idx[1]]
            
            if time_coast + place["takenTime"] <= time_limit + 30:
                path.append(place)
                score_sum += place_idx[0]
                place_idx_list.append(place_idx)
                time_coast += place["takenTime"]
                # 이동시간 추가
                time_coast += params["move_time"]

                # place_list의 원소들의 인덱스가 place_score_list로써 저장되어 있음 -> place_list는 건들면 안됨 -> None으로 바꾸는 방법
                del place_score_list_not_in_path[popper]
                place_list_not_in_path[place_idx[1]] = None
    
    
    return path, time_coast, score_sum, place_idx_list, params["enough_place"]