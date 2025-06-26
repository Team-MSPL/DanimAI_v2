
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


