import numpy as np

def reward_fn(result_eval, user_context):
    """
    result_eval = {
        place_score_avg_list: [...],
        geo_score_list: [...],
        diversity_score: 0.xx,
        popular_scores_list: [{mean, std, skew}, ...]
    }
    user_context:
        region
        distance_sensitivity (0~10)
        popular_sensitivity (0~10)
        n_day
    """

    # 기본 평가값
    mean_place = np.mean(result_eval["place_score_avg_list"])
    mean_geo   = np.mean(result_eval["geo_score_list"])
    div_score  = result_eval["diversity_score"]
    pop_score  = np.mean([p["mean"] for p in result_eval["popular_scores_list"]])

    # 조합 가능 (가중치 조절 가능)
    reward = (
        mean_place * 1.0 +
        mean_geo   * 1.0 +
        div_score  * 0.8 +
        pop_score  * 0.5
    )

    # return reward

    # --- 사용자의 조건을 반영한 보정값 ---
    distance_bias = user_context["distance_sensitivity"] / 10.0  # 0~1
    popular_bias  = user_context["popular_sensitivity"] / 10.0   # 0~1
    long_trip_bias = min(user_context["n_day"] / 5, 1.5)         # 여행일수 보정

    # 여행 하루수 많으면 다양한 장소를 더 담을 수 있음 -> diversity 조금 강화
    adjusted_reward = reward * long_trip_bias
    adjusted_reward += div_score * long_trip_bias * 0.2

    # 인기민감도 높으면 pop_score 가 더 중요
    adjusted_reward += pop_score * popular_bias * 0.3

    # 거리민감도 낮으면 geo_score(동선 최적화)가 더 중요
    adjusted_reward += mean_geo * (1 - distance_bias) * 0.3

    return adjusted_reward
