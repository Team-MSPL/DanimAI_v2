import numpy as np
from ..common.constant import WEIGHT, RESULT_NUM, DISTANCE_BIAS
from ..logging_config import logger
import math

def get_place_score_list(place_feature_matrix, theme_matrix, selected_theme_num_list, activated_theme_num, place_list, popular_sensitivity, version):
    try:
        max_tendency_len = 9
        if version == 3:
            max_tendency_len = 11
            
                    
        # 인기도 가중치 매핑: -25 ~ 75
        mapped_tail_weight = -25 + (popular_sensitivity / 10) * 100

        # WEIGHT는 2차원 배열 → numpy로 변환 후 수정
        weight = np.array(WEIGHT)

        try:
            # 맨 뒤 5번째 항목(인덱스 4)을 사용자 기반 값으로 덮어쓰기
            weight[:, 4] = weight[:, 4] * (mapped_tail_weight / 25)  # 비율로 조정 ( constant.py에서 스케일링 했기에 )
        except Exception as error:
            logger.error(f"인기도 가중치 설정 중 오류 발생 :, {error}")

        weight = weight.reshape(1, RESULT_NUM, 5)
        weight = np.repeat(weight, max_tendency_len, axis=0)
        weight = np.transpose(weight, (1, 2, 0))
        distanceBias = np.array(DISTANCE_BIAS)
        # distanceBias = weight * theme_matrix
        # distanceBias = np.sum(distanceBias, axis=2)
        # distanceBias = np.sum(distanceBias, axis=1)

        score_list = []
        preference_list = place_feature_matrix * theme_matrix
        index = np.arange(0, len(preference_list), 1, dtype=int)
        index= index.reshape(len(preference_list), 1)

        for w in weight:
            score = preference_list * w
            score = np.sum(score, axis=2)
            score = score / selected_theme_num_list
            score = np.nan_to_num(score)    # nan -> 0 변환, 윗줄에서 0으로 나눠 아래 문제가 생기더라도 여기서 처리해 줌
            # /home/ubuntu/DanimAI_v2/AI/ai/place_score.py:21: RuntimeWarning: invalid value encountered in divide
            #   score = score / selected_theme_num_list
            score = np.sum(score, axis=1)
            score /= activated_theme_num
            score = np.array(score, dtype=object)
            score = np.reshape(score, (len(preference_list),1))

            # 인덱스를 score에 추가
            score = np.append(score, index, axis=1)

            # place_list에서 관광지 이름을 추출해 score에 추가 - [점수계산결과, 인덱스, 관광지 이름] 형태
            place_names = np.array([place["name"] for place in place_list]).reshape(len(preference_list), 1)
            score = np.append(score, place_names, axis=1)  # 관광지 이름 추가
            
            score_list.append(score)
    except Exception as error:
        logger.info(f"관광지 데이터셋을 읽어오는 중에 오류가 발생했습니다:, {error}")
        logger.info(f"관광지역 첫번째 관광지:, {place_list[0]}")
        logger.info(f"관광지역 마지막 관광지:, {place_list[-1]}")

        
    return score_list, distanceBias


# 하버사인 공식: 위도와 경도를 이용하여 두 지점 간의 구면 거리 계산
def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # 지구 반지름 (단위: km)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c