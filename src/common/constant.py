from typing import Final

RESULT_NUM : Final = 5

WEIGHT : Final = []
DISTANCE_BIAS : Final = []
for n in range(RESULT_NUM):
    WEIGHT.append([i * (15 - n) for i in [40, 200, 200, 200, 20]])
    DISTANCE_BIAS.append(0.005 * (15 - n))
