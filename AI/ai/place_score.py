import numpy as np
from ..common.constant import WEIGHT, RESULT_NUM
from ..logging_config import logger
def get_place_score_list(place_feature_matrix, theme_matrix, selected_theme_num_list, activated_theme_num, place_list):
    try:
        weight = np.array(WEIGHT)

        weight = weight.reshape(1, RESULT_NUM, 5)
        weight = np.repeat(weight, 9, axis=0)
        weight = np.transpose(weight, (1, 2, 0))
        distanceBias = weight * theme_matrix
        distanceBias = np.sum(distanceBias, axis=2)
        distanceBias = np.sum(distanceBias, axis=1)

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
