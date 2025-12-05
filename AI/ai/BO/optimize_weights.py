# optimize_weights.py

"""
1. 강화 학습 (RL), 2. 베이지안 최적화 (BO)

기존 코스를 강화학습시키는 것이 아니라,
코스 평가 결과의 점수를 통해 weight를 강화학습시키는 구조

코스 생성은 기존 API 내부에서 수행
result_eval만 가지고 BO/RL을 돌림
BO는 단순히 “이 result_eval이면 가중치가 얼만큼 좋아야 한다”를 학습
BO가 출력한 params는 다음 API 호출에서 사용하는 weight로 주입

build_constants_from_params는 실제 코스 생성 단계에서 기존 constant 대신 호출

"""


from .agent_bo import BOAgent
from .reward import reward_fn
from .rl_runner import CourseRL
from .constant_template import save_params

#def optimize_weights():
def optimize_weights(result_eval):

    # ----------- 예외 처리 -----------
    if not result_eval or len(result_eval) == 0:
        print("[WARN] result_eval is empty. Skipping optimization...")

        # 디폴트 파라미터 반환
        default_params = {
            "w1": 100, "w2": 200, "w3": 200, "w4": 200, "w5": 25,
            "distance_bias": 10000
        }

        return default_params
    # ---------------------------------

    # 탐색 범위 정의
    dimensions = [
        (0, 200),     # w1
        (0, 300),     # w2
        (0, 300),     # w3
        (0, 300),     # w4
        (0, 50),      # w5
        (1000, 20000) # distance_bias
    ]

    agent = BOAgent(dimensions)

    rl = CourseRL(reward_fn)

    history = rl.run(agent, result_eval, episodes=40)

    # 최적 결과 보고 (BOOptimizer 내부 값 확인)
    best = agent.best()

    print("\n=== BEST RESULT ===")
    print(history)
    print(best)
    best_params = best["params"]
    
    # 저장
    save_params(best_params)

    return best_params

