import numpy as np
import hdbscan
from scipy.spatial.distance import cdist
from ..logging_config import logger
from sklearn.preprocessing import StandardScaler, RobustScaler
import copy
        
def cluster_with_hdbscan(places_to_cluster, target_cluster_count, min_cluster_size, max_cluster_size):
    
    if target_cluster_count == 1:
        return places_to_cluster, True
    
    # elif target_cluster_count == 2:
    #     return [places_to_cluster[0:min_cluster_size], places_to_cluster[min_cluster_size + 1:]], True
    
    coordinates = np.array([[place['lat'], place['lng']] for place in places_to_cluster])    
    
    # 위도는 1도당 약 111km, 경도는 위도에 따라 변하므로 이를 고려해서 조정
    lat_lon = np.copy(coordinates)
    lat_lon[:, 1] = lat_lon[:, 1] * np.cos(np.radians(lat_lon[:, 0]))  # 경도를 위도에 맞게 보정

    # 스케일링하여 클러스터링 성능 향상 - 위도, 경도는 너무 오밀조밀하게 모여있음
    scaler = StandardScaler()
    scaled_coordinates = scaler.fit_transform(lat_lon)
    
    # 초기 클러스터링 수행
    clustering = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size, min_samples=1)
    labels = clustering.fit_predict(scaled_coordinates)
    
    # Post-process to assign noise points
    unique_clusters = set(labels[labels >= 0])  # Exclude noise (-1)
    cluster_centers = [
        coordinates[labels == cluster_id].mean(axis=0) for cluster_id in unique_clusters
    ]
    
    # 모든 점을 노이즈로 볼 때 - 데이터 갯수가 너무 적거나
    if len(cluster_centers) == 0:
        # RobustScaler로 스케일링 다시 (중앙값과 IQR 사용)
        scaler = RobustScaler()
        scaled_coordinates = scaler.fit_transform(lat_lon)
        
        clustering = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size, min_samples=1)
        labels = clustering.fit_predict(scaled_coordinates)
        
        unique_clusters = set(labels[labels >= 0])  # Exclude noise (-1)
        cluster_centers = [
            coordinates[labels == cluster_id].mean(axis=0) for cluster_id in unique_clusters
        ]
        
        # 스케일러 바꿔도 안되면, 그냥 구간 쪼개서 리턴 - min_cluster_size만큼씩
        if len(cluster_centers) == 0:
            result = []
            for i in range(target_cluster_count):
                result.append(places_to_cluster[i * min_cluster_size : ((i+1) * min_cluster_size) - 1])
            return result, False
    
    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:  # 노이즈가 발생하면, 가장 가까운 클러스터에 삽입
            distances = cdist([coordinates[idx]], cluster_centers)  # Distances to cluster centers
            nearest_cluster = np.argmin(distances)  # Find nearest cluster
            labels[idx] = list(unique_clusters)[nearest_cluster]  # Assign to nearest cluster
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(places_to_cluster[idx])
    
    # 클러스터 수가 목표 수보다 적으면 클러스터 수를 증가시키고, 많으면 감소시킴
    current_cluster_count = len(clusters)
    
    if current_cluster_count > target_cluster_count:
        # 클러스터 수가 너무 많으면 제일 작은 클러스터를 쪼개서 병합 ( 한 클러스터에 든 장소가 적으면 )
        new_clusters = copy.deepcopy(clusters)
        while len(new_clusters) > target_cluster_count:
            new_clusters = split_smallest_cluster_and_reassign(new_clusters)
        return list(new_clusters.values()), True
    elif current_cluster_count < target_cluster_count:
        # 클러스터 수가 너무 적으면 제일 큰 클러스터를 쪼개서 클러스터 갯수의 균형을 맞춤 ( 한 클러스터에 든 장소가 많으면 )
        new_clusters = copy.deepcopy(clusters)
        while len(new_clusters) < target_cluster_count:
            new_clusters = split_largest_clusters(new_clusters)
        return list(new_clusters.values()), True
    
    # 이미 목표 클러스터 수와 일치하면 그대로 반환
    return list(clusters.values()), True

def split_smallest_cluster_and_reassign(clusters):
    # 가장 작은 클러스터를 찾아 분할
    smallest_cluster_id = min(clusters, key=lambda k: len(clusters[k]))
    smallest_cluster = copy.deepcopy(clusters[smallest_cluster_id])
    del clusters[smallest_cluster_id]
    
    # 클러스터의 중심 계산
    coordinates = np.array([[place['lat'], place['lng']] for place in smallest_cluster])
    center = coordinates.mean(axis=0)
    
    # 각 장소가 가장 가까운 클러스터에 속하도록 분할
    cluster_centers = {k: np.mean([[place['lat'], place['lng']] for place in v], axis=0) for k, v in clusters.items()}
    
    # 새로운 클러스터 생성: 기존 클러스터의 장소들을 가장 가까운 다른 클러스터로 재배치
    new_clusters = {}
    
    for place in smallest_cluster:
        # 각 장소가 가장 가까운 클러스터 찾기
        place_coords = np.array([place['lat'], place['lng']])
        closest_cluster_id = min(cluster_centers, key=lambda k: np.linalg.norm(place_coords - cluster_centers[k]))
        
        if closest_cluster_id not in new_clusters:
            new_clusters[closest_cluster_id] = []
        
        new_clusters[closest_cluster_id].append(place)
    
    # 작은 클러스터는 삭제하고, 새로운 클러스터를 추가
    clusters.update(new_clusters)
    
    return clusters

def split_largest_clusters(clusters):
    # 클러스터가 너무 크면 하나로 나눠서 더 많은 클러스터를 생성
    cluster_ids = list(clusters.keys())
    largest_cluster_id = max(cluster_ids, key=lambda x: len(clusters[x]))
    
    # 가장 큰 클러스터를 가져옴
    large_cluster = copy.deepcopy(clusters[largest_cluster_id])
    coordinates = np.array([[place['lat'], place['lng']] for place in large_cluster])
    
    # 클러스터의 중심을 계산
    center = coordinates.mean(axis=0)
    
    # 각 장소와 중심점 간의 거리 계산
    distances_to_center = np.linalg.norm(coordinates - center, axis=1)
    
    # 중심에 가까운 그룹과 멀리 있는 그룹으로 나누기
    median_distance = np.median(distances_to_center)
    
    # 중심에 가까운 클러스터와 먼 클러스터로 분할
    group1 = [large_cluster[i] for i in range(len(large_cluster)) if distances_to_center[i] <= median_distance]
    group2 = [large_cluster[i] for i in range(len(large_cluster)) if distances_to_center[i] > median_distance]
    
    # 나눈 클러스터들 추가
    del clusters[largest_cluster_id]
    
    new_cluster_id1 = largest_cluster_id * 2
    new_cluster_id2 = largest_cluster_id * 2 + 1
    
    clusters[new_cluster_id1] = group1
    clusters[new_cluster_id2] = group2
    
    return clusters