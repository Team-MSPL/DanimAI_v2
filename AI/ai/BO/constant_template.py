# constant_template.py
"""
constant.py를 RL/BO가 override할 수 있도록 템플릿 형태로 분리
user_context별로 weight를 저장/로드 가능하도록 수정

1. 강화 학습 (RL), 2. 베이지안 최적화 (BO)

기존 코스를 강화학습시키는 것이 아니라,
코스 평가 결과의 점수를 통해 weight를 강화학습시키는 구조

코스 생성은 기존 API 내부에서 수행
result_eval만 가지고 BO/RL을 돌림
BO는 단순히 “이 result_eval이면 가중치가 얼만큼 좋아야 한다”를 학습
BO가 출력한 params는 다음 API 호출에서 사용하는 weight로 주입

build_constants_from_params는 실제 코스 생성 단계에서 기존 constant 대신 호출

"""

import json
import os

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


# -------------------------------
# build_constants_from_params
# (user_context 필요!)
# -------------------------------
def build_constants_from_params(user_context):
    """
    params: dict
      {
        "w1": ..., "w2": ..., "w3": ..., "w4": ..., "w5": ...,
        "distance_bias": ...
      }
    """
    
    params = load_params(user_context)
    if params is None:
        #default_params
        params = {
            "w1": 100, "w2": 200, "w3": 200, "w4": 200, "w5": 25,
            "distance_bias": 10000
        }

    WEIGHT = [
        #[params["w1"], params["w2"], params["w3"], params["w4"], params["w5"]]
        [(((n + idx) % RESULT_NUM + 1) ** n) * item * (RESULT_NUM - n) for idx, item in enumerate(params["w1"], params["w2"], params["w3"], params["w4"], params["w5"])]
        for n in range(RESULT_NUM)
    ]
    DISTANCE_BIAS = [
        params["distance_bias"] * (RESULT_NUM - n)
        for n in range(RESULT_NUM)
    ]

    return WEIGHT, DISTANCE_BIAS

# -------------------------------
# load_params (context별)
# -------------------------------
def load_params(user_context):
    key = make_context_key(user_context)

    if not os.path.exists(STORE_PATH):
        return None

    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except:
        return None

    return db.get(key, None)


# -------------------------------
# save_params (context별 저장)
# -------------------------------
def save_params(params, user_context):
    key = make_context_key(user_context)

    db = {}
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except:
            db = {}

    db[key] = params

    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)