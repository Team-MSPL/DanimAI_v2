# constant_template.py
"""
constant.py를 RL/BO가 override할 수 있도록 템플릿 형태로 분리

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

def build_constants_from_params():
    """
    params: dict
      {
        "w1": ..., "w2": ..., "w3": ..., "w4": ..., "w5": ...,
        "distance_bias": ...
      }
    """
    
    params = load_params()
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

def load_params():
    if not os.path.exists(STORE_PATH):
        return None
    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except:
        return None

def save_params(params):
    with open(STORE_PATH, "w") as f:
        json.dump(params, f, indent=2)
