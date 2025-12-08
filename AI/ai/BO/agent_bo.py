# agent_bo.py
from skopt import Optimizer
import random
import numpy as np

# explore 20%, exploit 80%

class BOAgent:
    def __init__(self, dimensions, explore_ratio=0.2):
        self.optimizer = Optimizer(dimensions)
        self.past = []
        self.explore_ratio = explore_ratio
        self.dimensions = dimensions

    def sample_params(self):
        """exploit (BO ask) 와 explore(perturbation) 혼합"""
        if random.random() < self.explore_ratio or len(self.past) == 0:
            # ---- EXPLORATION: 임의 perturbation ----
            params = []
            for dim in self.dimensions:
                low, high = dim
                params.append(random.uniform(low, high))
            return params

        # ---- EXPLOITATION: BO 최적 탐색 ----
        return self.optimizer.ask()

    def update(self, params, reward, user_context):
        """BO는 보상이 크면 좋으므로 -reward"""
        self.optimizer.tell(params, -reward)
        self.past.append({"params": params, "reward": reward, "context": user_context})

    def best(self):
        if not self.past:
            return None
        return max(self.past, key=lambda x: x["reward"])