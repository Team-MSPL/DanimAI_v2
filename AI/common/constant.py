from typing import Final

# 코스 최대 갯수
RESULT_NUM : Final = 4

WEIGHT : Final = []
DISTANCE_BIAS : Final = []
for n in range(RESULT_NUM):
    WEIGHT.append([i * (RESULT_NUM - n) for i in [40, 200, 200, 200, 20]])
    DISTANCE_BIAS.append(0.005 * (15 - n))

MAX_DISTANCE_SENSITIVITY :Final = 10
PUBLIC_COEFF :Final = 10
CAR_COEFF :Final = 5

CAR_TRANSIT = 30
PUBLIC_TRANSIT = 60

# 반복문 돌리는 횟수 ( 힐클라임 최대 횟수 )
HILL_LIMIT = 10000
HILL_SWITCH_LIMIT = 200

class Dummy:
    PARTNER = [0, 0, 0, 0, 0, 0, 0]
    PLAY = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    CONCEPT = [0, 0, 0, 0, 0, 0]
    TOUR = [0, 0, 0, 0, 0, 0, 0, 0]
    SEASON = [0, 0, 0, 0]
