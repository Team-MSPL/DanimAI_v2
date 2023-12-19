import numpy as np
from src.common.constant import WEIGHT, RESULT_NUM
def get_place_score_list(place_list, theme_list, selected_theme_num_list, activated_theme_num):
    weight = np.array(WEIGHT)

    weight = weight.reshape(1, RESULT_NUM, 5)
    weight = np.repeat(weight, 9, axis=0)
    weight = np.transpose(weight, (1, 2, 0))
    distanceBias = weight * theme_list
    distanceBias = np.sum(distanceBias, axis=2)
    distanceBias = np.sum(distanceBias, axis=1)

    score_list = []
    preference_list = place_list * theme_list
    for w in weight:
        score = preference_list * w
        score = np.sum(score, axis=2)
        score = score / selected_theme_num_list
        score = np.nan_to_num(score)
        score = np.sum(score, axis=1)
        score /= activated_theme_num
        score_list.append(score)

    score_list = np.array(score_list)

    return score_list, distanceBias
