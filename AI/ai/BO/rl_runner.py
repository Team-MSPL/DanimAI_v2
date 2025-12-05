class CourseRL:
    def __init__(self, reward_fn):
        # env_fn 대신 result_eval 직접 입력받게
        #self.env_fn = env_fn
        self.reward_fn = reward_fn

    def run(self, agent, result_eval, user_context, episodes=30):
        history = []

        for ep in range(episodes):
            params = agent.sample_params()

            # env 실행 → 평가 점수
            #result_eval = self.env_fn(params)
            # env_fn 대신 result_eval 직접 입력받게

            # 보상 계산
            reward = self.reward_fn(result_eval, user_context)

            # agent 업데이트
            agent.update(params, reward)

            history.append({
                "episode": ep,
                "params": params,
                "reward": reward
            })

            print(f"[EP {ep}] reward={reward:.4f} params={params}")

        return history
