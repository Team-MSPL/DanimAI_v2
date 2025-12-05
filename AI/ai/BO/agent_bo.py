# agent_bo.py
from skopt import Optimizer

class BOAgent:
    def __init__(self, dimensions):
        self.optimizer = Optimizer(dimensions)
        self.past = []  # (params, reward) 저장

    def sample_params(self):
        params = self.optimizer.ask()
        return params

    def update(self, params, reward, user_context):
        self.optimizer.tell(params, -reward)  # reward가 높을수록 좋도록 -reward
        self.past.append({"params": params, "reward": reward, "context": user_context})

    def best(self):
        return max(self.past, key=lambda x: x["reward"])
