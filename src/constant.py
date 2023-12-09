from typing import Final

RESULT_NUM : Final = 7

WEIGHT : Final = []
for n in range(RESULT_NUM):
    WEIGHT.append([i * (15 - n) for i in [40, 200, 200, 200, 20, 0.005]])
