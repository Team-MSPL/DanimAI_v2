from typing import Final

RESULT_NUM : Final = 1

WEIGHT : Final = []
DISTANCE_BIAS : Final = []
for n in range(RESULT_NUM):
    WEIGHT.append([i * (15 - n) for i in [40, 200, 200, 200, 20]])
    DISTANCE_BIAS.append(0.005 * (15 - n))

MAX_DISTANCE_SENSITIVITY :Final = 10
PUBLIC_COEFF :Final = 10
CAR_COEFF :Final = 5

CAR_TRANSIT = 30
PUBLIC_TRANSIT = 60