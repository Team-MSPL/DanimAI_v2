import numpy as np
import copy
import math
from ..common.constant import LARGE_NUMBER
from ..logging_config import logger
from python_tsp.heuristics import solve_tsp_local_search

def tsp(path):
    
    if len(path) == 2:
        lat_diff = path[0]["lat"] - path[1]["lat"]
        lon_diff = path[0]["lng"] - path[1]["lng"]
        return path, math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
        
    # 참조 오류 해결을 위함 - tsp에서는 순서가 섞이기에 참조하던 원본 path가 유지되지 않을 수 있음
    copy_path = copy.deepcopy(path)
    
    # 맨 앞 + 맨 뒤에 숙소가 있는 경우 처리
    if path[-1]["is_accomodation"] and path[0]["is_accomodation"]:
    
        ts_path, distance = tsp_fixed_accomodation_both(copy_path)
        return ts_path, distance
    
    # 맨 앞 or 맨 뒤에 숙소가 있는 경우 처리 ( 한쪽만 )
    elif path[-1]["is_accomodation"] or path[0]["is_accomodation"]:
    
        ts_path, distance = tsp_fixed_accomodation(copy_path)
        return ts_path, distance
    
    else:
        # ts_path, distance = tsp_common(copy_path)
        ts_path, distance = find_greedy_path_outside_to_closest(copy_path)
        
        return ts_path, distance


def find_greedy_path_outside_to_closest(path):
    def calculate_distance(place1, place2):
        """Calculate Euclidean distance between two places."""
        lat_diff = place1["lat"] - place2["lat"]
        lng_diff = place1["lng"] - place2["lng"]
        return math.sqrt(lat_diff**2 + lng_diff**2)

    # Step 1: Calculate the center point of all places
    total_lat = sum(place["lat"] for place in path)
    total_lng = sum(place["lng"] for place in path)
    center_lat = total_lat / len(path)
    center_lng = total_lng / len(path)
    center_point = {"lat": center_lat, "lng": center_lng}
    
    # Step 2: Find the outermost starting point (farthest from the center)
    max_distance = -float("inf")
    start_place = None
    for place in path:
        distance_from_center = calculate_distance(place, center_point)
        if distance_from_center > max_distance:
            max_distance = distance_from_center
            start_place = place
    
    # Step 3: Initialize
    unvisited = path[:]
    unvisited.remove(start_place)
    current_place = start_place
    greedy_path = [current_place]
    total_distance = 0
    
    # Step 4: Greedily connect to the nearest unvisited place
    while unvisited:
        nearest_place = min(unvisited, key=lambda place: calculate_distance(current_place, place))
        distance_to_nearest = calculate_distance(current_place, nearest_place)
        total_distance += distance_to_nearest
        greedy_path.append(nearest_place)
        unvisited.remove(nearest_place)
        current_place = nearest_place

    return greedy_path, total_distance
#일반적인 경우의 tsp
def tsp_common(path):
    
    len_path = len(path)
    
    # 거리 행렬 제작
    distance_matrix = [[0 for _ in range(len_path)] for _ in range(len_path)]
    for i in range(len_path):
        for j in range(len_path):
            lat_diff = path[i]["lat"] - path[j]["lat"]
            lon_diff = path[i]["lng"] - path[j]["lng"]
            distance_matrix[i][j] = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    distance_matrix = np.array(distance_matrix)
    
    
    # 가장 긴 경로 탐색
    max_distance = -1
    max_pair = (0, 0)
    for i in range(len_path):
        for j in range(len_path):
            if distance_matrix[i][j] > max_distance:
                max_distance = distance_matrix[i][j]
                max_pair = (i, j)
    
    # 가장 긴 경로 제거 (큰 값을 무한대 대체)
    distance_matrix[max_pair[0]][max_pair[1]] = float('inf')
    distance_matrix[max_pair[1]][max_pair[0]] = float('inf')
    
    # TSP 계산 (긴 경로 제거한 상태)
    permutation, distance = solve_tsp_local_search(distance_matrix)
    
    # 제거된 경로의 거리 다시 추가
    distance += max_distance
    
    # 최종 경로 재구성
    ts_path = [path[i] for i in permutation]
    
    
    # # 디버깅용 거리 출력
    # total_distance = 0
    # segment_distance_list = []
    # for i in range(len(ts_path) - 1):
    #     current_index = permutation[i]
    #     next_index = permutation[i + 1]
    #     segment_distance = distance_matrix[current_index][next_index]
    #     segment_distance_list.append(segment_distance)
    #     total_distance += segment_distance    
    # logger.info(f"Distances between points in the selected path:: {segment_distance_list}")
    
    
    
    return ts_path, distance
    
    # # tsp 라이브러리 실행
    # permutation, distance = solve_tsp_local_search(distance_matrix)
    
    # #tsp는 원점 회귀 이기 때문에, 마지막 노드에서 첫 노드로 돌아오는 거리는 빼 줘야 함
    # start = permutation[0]
    # end = permutation[-1]
    # lat_diff = path[start]["lat"] - path[end]["lat"]
    # lon_diff = path[start]["lng"] - path[end]["lng"]
    # distance -= math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    
    # # 최종 경로를 permutation 순서에 맞게 재구성
    # ts_path = [path[i] for i in permutation]
    
    # # 첫 노드와 두 번째 노드, 첫 노드와 마지막 노드 간 거리 비교
    # start = permutation[0]
    # second = permutation[1]
    # end = permutation[-1]
    
    # dist_start_to_second = distance_matrix[start][second]
    # dist_start_to_end = distance_matrix[start][end]
    
    # # tsp는 원점 회귀 이기 때문에, 마지막 노드에서 첫 노드로 돌아오는 거리는 빼 줘야 함
    # # 첫 관광지에서 두 번째 관광지로의 거리 > 첫 관광지에서 마지막 관광지로의 거리인 경우 역순 경로 생성
    # # 1-2-3-4 에서 1-2간 거리 > 1-4간 거리 => 1-4-3-2가 더 빠름
    # if dist_start_to_second > dist_start_to_end:
    #     reversed_part = list(reversed(ts_path[1:]))  # 첫 장소를 제외하고 역순으로
    #     ts_path = [ts_path[0]] + reversed_part  # 첫 장소를 고정
    #     # 거리 재계산
    #     distance = 0
    #     for i in range(len(ts_path) - 1):
    #         current_index = path.index(ts_path[i])
    #         next_index = path.index(ts_path[i + 1])
    #         distance += distance_matrix[current_index][next_index]
            
    # return ts_path, distance

# 맨 앞 or 맨 뒤에 숙소가 있는 경우 처리 ( 한쪽만 )
def tsp_fixed_accomodation(path):
    
    start_accommodation, end_accommodation = None, None
            
    # 숙소의 위치가 바뀌는 경우 대비
    if path[-1]["is_accomodation"]:
        end_accommodation = path[-1]
    elif path[0]["is_accomodation"]:
        start_accommodation = path[0]
    
    len_path = len(path)
        
    # 거리 행렬 계산
    distance_matrix = [[0 for _ in range(len_path)] for _ in range(len_path)]
    for i in range(len_path):
        for j in range(len_path):
            lat_diff = path[i]["lat"] - path[j]["lat"]
            lon_diff = path[i]["lng"] - path[j]["lng"]
            distance_matrix[i][j] = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
                
            
            
    # 숙소가 있으면 그 숙소까지의 distance에 LARGE_NUMBER를 더해주는 방식 ( 맨 앞 or 맨 뒤는 고정하려고)

    # 시작점과 끝점이 다른 노드로 가는 거리 반영 + 나머지 노드는 LARGE_NUMBER로 처리 -> 맨 앞과 맨 뒤에 모두 숙소가 있을 경우 서로 간의 거리는 2 * LARGENUMBER + 실제 거리    
    if path[0]["is_accomodation"]:
        for i in range(1, len_path):
            # 시작점에서 중간 지점으로 가는 거리
            distance_matrix[0][i] = distance_matrix[0][i] + LARGE_NUMBER  # start에서 중간 노드까지 거리 + LARGE_NUMBER
            distance_matrix[i][0] = distance_matrix[i][0] + LARGE_NUMBER
        
    elif path[-1]["is_accomodation"]:
        for i in range(0, len_path - 1):
            # 끝점에서 중간 지점으로 가는 거리 유지
            distance_matrix[-1][i] = distance_matrix[-1][i] + LARGE_NUMBER  # end에서 중간 노드까지 거리 + LARGE_NUMBER
            distance_matrix[i][-1] = distance_matrix[i][-1] + LARGE_NUMBER
    
    # TSP 실행
    distance_matrix = np.array(distance_matrix)
    permutation, distance = solve_tsp_local_search(distance_matrix)
    
    # 숙소의 위치가  바뀌었을 수도 있음 - 이 경우 permutation을 분해 및 재결합해준다. ( permutation : 원본 path의 index값들을 tsp의 결과로 정렬해놓음. 예) [0, 3, 1, 2] )
    
    if end_accommodation is not None and permutation[-1] != len_path - 1:
        #맨 뒤가 아니므로 + 1 해줘도 인덱스 오류가 안생김
        new_permutation = permutation[permutation.index(len_path - 1) + 1:] + permutation[:permutation.index(len_path - 1) + 1]
        #print("tsp에서 end 숙소의 위치가 바뀜", permutation, new_permutation)
        permutation = new_permutation
    
    # 여러번 시도해보았으나, start 숙소는 고정 잘 되는 듯, 아직 테스트 단계라 냅둠
    elif start_accommodation is not None and permutation[0] != 0:
        new_permutation = permutation[permutation.index(0):] + permutation[:permutation.index(0)]
        logger.info("tsp에서 start 숙소의 위치가 바뀜", permutation, new_permutation)
        permutation = new_permutation
        
        
    #tsp는 원점 회귀 이기 때문에, 마지막 노드에서 첫 노드로 돌아오는 거리는 빼 줘야 함
    start = permutation[0]
    end = permutation[-1]
    lat_diff = path[start]["lat"] - path[end]["lat"]
    lon_diff = path[start]["lng"] - path[end]["lng"]
    distance -= math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    
    # 최종 경로를 permutation 순서에 맞게 재구성
    ts_path = [path[i] for i in permutation]
    

    return ts_path, distance


# 맨 앞 + 맨 뒤에 숙소가 있는 경우 처리
def tsp_fixed_accomodation_both(path):
    
            
    # 숙소의 위치가 바뀌는 경우 대비
    start_accommodation, end_accommodation = path[0], path[-1]
    
    len_path = len(path)
        
    # 거리 행렬 계산
    distance_matrix = [[0 for _ in range(len_path)] for _ in range(len_path)]
    for i in range(len_path):
        for j in range(len_path):
            lat_diff = path[i]["lat"] - path[j]["lat"]
            lon_diff = path[i]["lng"] - path[j]["lng"]
            distance_matrix[i][j] = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
                
            
            
    # 숙소가 있으면 그 숙소까지의 distance에 LARGE_NUMBER를 더해주는 방식 ( 맨 앞 or 맨 뒤는 고정하려고)

    # 시작점과 끝점이 다른 노드로 가는 거리 반영 + 나머지 노드는 LARGE_NUMBER로 처리 -> 맨 앞과 맨 뒤에 모두 숙소가 있을 경우 서로 간의 거리는 2 * LARGENUMBER + 실제 거리    

    for i in range(1, len_path):
        # 시작점에서 중간 지점으로 가는 거리
        distance_matrix[0][i] = distance_matrix[0][i] + LARGE_NUMBER  # start에서 중간 노드까지 거리 + LARGE_NUMBER
        distance_matrix[i][0] = distance_matrix[i][0] + LARGE_NUMBER
        # 끝점에서 중간 지점으로 가는 거리 유지
        distance_matrix[-1][i] = distance_matrix[-1][i] + LARGE_NUMBER  # end에서 중간 노드까지 거리 + LARGE_NUMBER
        distance_matrix[i][-1] = distance_matrix[i][-1] + LARGE_NUMBER
        
    
    # TSP 실행
    distance_matrix = np.array(distance_matrix)
    permutation, distance = solve_tsp_local_search(distance_matrix)
    
    # 숙소의 위치가  바뀌었을 수도 있음 - LARGE_NUMBER 때문에 두 숙소는 무조건 붙어 다니므로, 그 가운데를 잘라서 나눔 ( permutation : 원본 path의 index값들을 tsp의 결과로 정렬해놓음. 예) [0, 3, 1, 2] )        
    if end_accommodation is not None and permutation[-1] != len_path - 1:
        # 예 : [0, 3, 1, 2] -> [3, 1, 2] + [0] -> 뒤집기 -> [0, 2, 1, 3]
        new_permutation = permutation[permutation.index(len_path - 1):] + permutation[:permutation.index(len_path - 1)]
        new_permutation.reverse()
        #print("tsp에서 양쪽 숙소의 위치가 바뀜", permutation, new_permutation)
        permutation = new_permutation
            
        
    #tsp는 원점 회귀 이기 때문에, 마지막 노드에서 첫 노드로 돌아오는 거리는 빼 줘야 함
    start = permutation[0]
    end = permutation[-1]
    lat_diff = path[start]["lat"] - path[end]["lat"]
    lon_diff = path[start]["lng"] - path[end]["lng"]
    distance -= math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    
    # 최종 경로를 permutation 순서에 맞게 재구성
    ts_path = [path[i] for i in permutation]
    

    return ts_path, distance