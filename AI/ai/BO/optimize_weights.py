# optimize_weights.py

"""
1. 강화 학습 (RL), 2. 베이지안 최적화 (BO)

기존 코스를 강화학습시키는 것이 아니라,
코스 평가 결과의 점수를 통해 weight를 강화학습시키는 구조

코스 생성은 기존 API 내부에서 수행
result_eval만 가지고 BO/RL을 돌림
BO는 단순히 “이 result_eval이면 가중치가 얼만큼 좋아야 한다”를 학습
BO가 출력한 params는 다음 API 호출에서 사용하는 weight로 주입

"""


from .agent_bo import BOAgent
from .reward import reward_fn
from .rl_runner import CourseRL
from .param_storage import load_context_params, save_context_params

RESULT_NUM = 7
STORE_PATH = "./best_params.json"

# -------------------------------
# 범주화(Binning) 함수
# -------------------------------
def bin_sensitivity(value):
    if value is None:
        return "none"
    if value <= 3:
        return "LOW"
    if value <= 6:
        return "MID"
    return "HIGH"
def n_day_sensitivity(value):
    if value is None:
        return "none"
    if value <= 2:
        return "SHORT"
    if value <= 5:
        return "MID"
    return "LONG"

# -------------------------------
# 키 생성: region + DIS_BIN + POP_BIN + n_day
# -------------------------------
def make_context_key(user_context):
    region = "_".join(user_context.get("region", [])) if isinstance(user_context.get("region"), list) else user_context.get("region", "none")
    
    dist = bin_sensitivity(user_context.get("distance_sensitivity"))
    pop  = bin_sensitivity(user_context.get("popular_sensitivity"))
    nday = n_day_sensitivity(user_context.get("n_day", "none"))

    return f"{region}_{dist}_{pop}_{nday}"


def safe_reward_fn(result_eval, user_context):
    # 필수 key 없으면 reward=0 반환
    required = ["place_score_avg_list", "geo_score_list", "diversity_score", "popular_scores_list"]
    for k in required:
        if k not in result_eval or result_eval[k] is None:
            return 0

    try:
        reward = reward_fn(result_eval, user_context)
        if np.isnan(reward) or reward is None:
            return 0
        return reward
    except:
        return 0



#def optimize_weights():
def optimize_weights(result_eval, user_context):
    """      
        result_eval = {
            "place_score_avg_list":place_score_avg_list,
            "geo_score_list":geo_score_list,
            "diversity_score":div_score,
            "popular_scores_list":popular_scores_list,            
        }
        user_context.update({
            "region": region_list,
            "select_list": select_list,
            "distance_sensitivity": distance_sensitivity,
            "popular_sensitivity": popular_sensitivity,
            "n_day": n_day,
            "transit": transit,
            "bandwidth": bandwidth,
            "enough_place": enough_place,
        })

    """
    # (1) result_eval 체크
    if not result_eval:
        print("[WARN] empty result_eval → skip")
        return None

    # (2) key 생성
    key = make_context_key(user_context)

    # (3) 저장된 best 가져오기
    stored = load_context_params(key)
    if stored:
        best_reward = stored["best_reward"]
        best_params = stored["params"]
    else:
        best_reward = float("-inf")
        best_params = None

    # (4) BO + RL 실행
    dimensions = [...]
    agent = BOAgent(dimensions)
    rl = CourseRL(safe_reward_fn)

    history = rl.run(agent, result_eval, user_context, episodes=40)

    # 새 best 찾기
    new_best = agent.best()
    if not new_best:
        return best_params  # fallback

    new_reward = new_best["reward"]
    new_params = new_best["params"]

    # (5) 비교 후 저장 여부 결정
    if new_reward > best_reward:
        print("🎉 Improved weights → save")
        save_context_params(key, new_params, new_reward)
        return new_params
    else:
        print("😐 No improvement → keep previous")
        return best_params
