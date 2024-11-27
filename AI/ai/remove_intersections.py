
from shapely.geometry import LineString
from ..logging_config import logger

# 1일차 코스, 2일차 코스끼리 연결하지 않는 경우 - O(n^2 * d^2)
def remove_routes_with_intersections(path):
    """
    전체 여행 코스에서 lat, lng 좌표를 사용해 선분을 만들고,
    하루별 경로끼리 교차 지점이 1개 이상인 코스를 삭제합니다.
    
    :param path: 3D 배열로 구성된 여행 코스 목록
    :return: 교차 지점이 1개 이상인 코스를 제거한 새로운 path 배열
    """
    def create_daily_line(day_path):
        """하루치 경로로부터 하나의 LineString 객체를 생성합니다."""
        coordinates = [(place['lat'], place['lng']) for place in day_path]
        return LineString(coordinates)

    def count_intersections(route):
        # 하루치 코스를 LineString으로 변환 - 당일치기일땐 필요 x
        daily_lines = [create_daily_line(day_path) for day_path in route if len(day_path) > 1]
        
        # 각 코스 간 교차 여부 확인
        intersections_count = 0
        for i in range(len(daily_lines)):
            for j in range(i + 1, len(daily_lines)):
                if daily_lines[i].intersects(daily_lines[j]):
                    intersections_count += 1
        return intersections_count
        
        # # 각 하루별로 선을 생성
        # for day_path in route:
        #     if len(day_path) <= 1:
        #         continue
            
        #     # 장소가 2개 이상일 경우에만 선을 생성
        #     coordinates = [(place['lat'], place['lng']) for place in day_path]
        #     if len(coordinates) > 1:
        #         for i in range(len(coordinates) - 1):
        #             line = LineString([coordinates[i], coordinates[i + 1]])
        #             daily_lines.append(line)
        
        # # 하루치 코스별 선 간의 교차 여부 확인
        # intersections_count = 0
        # for i in range(len(daily_lines)):
        #     for j in range(i + 1, len(daily_lines)):
        #         if daily_lines[i].intersects(daily_lines[j]):
        #             intersections_count += 1
        
        # return intersections_count

    # 교차 횟수가 1 이상인 코스를 제거하여 새로운 리스트 생성
    filtered_path = [route for route in path if count_intersections(route) < 1]
    
    if len(path) - len(filtered_path) > 0:
        logger.info("교차 횟수가 1 이상인 코스 제거 : %s 개", str(len(path) - len(filtered_path)))
    
    if len(filtered_path) == 0:
        filtered_path = [route for route in path if count_intersections(route) < 2]
        logger.info("교차 횟수가 2 이상인 코스 제거 : %s 개", str(len(path) - len(filtered_path)))
        if len(filtered_path) == 0:
            logger.info("교차 횟수가 2 이하인 코스가 없음")
            return path
        
    return filtered_path


# 하루치 코스 내에서의 비교 ( 의미 x )
# def remove_routes_with_intersections(path):
#     """
#     전체 여행 코스에서 lat, lng 좌표를 사용해 선분을 만들고,
#     교차 지점이 1개 이상인 코스를 삭제합니다.
    
#     :param path: 3D 배열로 구성된 여행 코스 목록
#     :return: 교차 지점이 1개 이상인 코스를 제거한 새로운 path 배열
#     """
#     def count_intersections(route):
#         # 전체 경로 좌표를 라인 세그먼트로 생성
#         coordinates = [(place['lat'], place['lng']) for day_path in route for place in day_path]
#         line = LineString(coordinates)
        
        
#         # 경로가 두 개 이상의 self-intersection이 있는지 확인
#         if line.is_simple:
#             return 0  # 교차가 없음
#         else:
#             intersections = line.intersection(line)
#             # 교차 지점의 개수를 반환 (MultiPoint일 경우 개수를, 그렇지 않으면 1 반환)
#             if intersections.geom_type == 'MultiPoint':
#                 return len(intersections)
#             elif intersections.geom_type == 'Point':
#                 return 1
#             else:
#                 return 0

#     # 교차 횟수가 1 이상인 코스를 제거하여 새로운 리스트 생성
#     filtered_path = [route for route in path if count_intersections(route) < 1]
    
#     if len(path) - len(filtered_path) > 0:
#         logger.info("교차 횟수가 1 이상인 코스 제거 - %s 개", str(len(path) - len(filtered_path)))
    
#     if len(filtered_path) == 0:
#         filtered_path = [route for route in path if count_intersections(route) < 2]
#         if len(filtered_path) == 0:
#             logger.info("교차 횟수가 2 이하이 코스가 없음")
#             return path
        
#     return filtered_path

# from shapely.geometry import LineString
# from ..logging_config import logger


# 모든 점을 이어서 교차점 탐색하는 방법
# def remove_routes_with_intersections(path):
#     """
#     전체 여행 코스에서 lat, lng 좌표를 사용해 선분을 만들고,
#     교차 지점이 1개 이상인 코스를 삭제합니다.
    
#     :param path: 3D 배열로 구성된 여행 코스 목록
#     :return: 교차 지점이 1개 이상인 코스를 제거한 새로운 path 배열
#     """
#     def count_intersections(route):
#         # 전체 경로 좌표를 라인 세그먼트로 생성
#         coordinates = [(place['lat'], place['lng']) for day_path in route for place in day_path]
#         line = LineString(coordinates)
        
#         # 경로가 두 개 이상의 self-intersection이 있는지 확인
#         if line.is_simple:
#             return 0  # 교차가 없음
#         else:
#             intersections = line.intersection(line)
#             return len(intersections) if intersections.geom_type == 'MultiPoint' else 1

#     def are_routes_intersecting(route1, route2):
#         # route1과 route2의 경로 좌표를 라인 세그먼트로 생성
#         coordinates1 = [(place['lat'], place['lng']) for day_path in route1 for place in day_path]
#         coordinates2 = [(place['lat'], place['lng']) for day_path in route2 for place in day_path]
#         line1 = LineString(coordinates1)
#         line2 = LineString(coordinates2)
#         return line1.intersects(line2)

#     # 교차 횟수가 1 이상인 코스를 제거하여 새로운 리스트 생성
#     filtered_path = []
#     for route in path:
#         has_intersection = False
#         # 현재 경로와 다른 모든 경로를 비교
#         for other_route in path:
#             if route != other_route and are_routes_intersecting(route, other_route):
#                 has_intersection = True
#                 break
#         if not has_intersection:
#             filtered_path.append(route)

#     if len(path) - len(filtered_path) > 0:
#         logger.info("교차 횟수가 1 이상인 코스 제거 : %s 개", str(len(path) - len(filtered_path)))
    
#     if len(filtered_path) == 0:
#         filtered_path = [route for route in path if count_intersections(route) < 2]
#         logger.info("교차 횟수가 2 이상인 코스 제거 : %s 개", str(len(path) - len(filtered_path)))
#         if len(filtered_path) == 0:
#             logger.info("교차 횟수가 2 이하인 코스가 없음")
#             return path
        
#     return filtered_path
