import numpy as np

def reward_fn(result_eval):
    """
    result_eval = {
        place_score_avg_list: [...],
        geo_score_list: [...],
        diversity_score: 0.xx,
        popular_scores_list: [{mean, std, skew}, ...]
    }
    """

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

    return reward
