from typing import Final

# 코스 최대 갯수
RESULT_NUM : Final = 7

WEIGHT : Final = []
DISTANCE_BIAS : Final = []
for n in range(RESULT_NUM):
    #WEIGHT.append([i * (RESULT_NUM - n) for i in [40, 200, 200, 200, 20]])
    WEIGHT.append([((n + idx) % RESULT_NUM + 1) * item * (RESULT_NUM - n) for idx, item in enumerate([40, 200, 200, 200, 20])])
    DISTANCE_BIAS.append(0.01 * (RESULT_NUM - n))

MAX_DISTANCE_SENSITIVITY :Final = 10
PUBLIC_COEFF :Final = 10
CAR_COEFF :Final = 5

CAR_TRANSIT = 30
PUBLIC_TRANSIT = 60

# 반복문 돌리는 횟수 ( 힐클라임 최대 횟수 )
HILL_LIMIT = 3000
HILL_SWITCH_LIMIT = 100

# 좌표간 거리 계산에 사용하는 큰 숫자 - 양 끝 노드 ( 숙소 )를 고정할 때 사용함
LARGE_NUMBER = 10000

class Dummy:
    PARTNER = [0, 0, 0, 0, 0, 0, 0]
    PLAY = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    CONCEPT = [0, 0, 0, 0, 0, 0]
    TOUR = [0, 0, 0, 0, 0, 0, 0, 0]
    SEASON = [0, 0, 0, 0]
