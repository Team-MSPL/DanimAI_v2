import copy
import traceback
from .logging_config import logger

def remakeTendency(old_tendency_data):  
    try:  
        # 기존 데이터 예제 - 점수도 가능 - 0~100점
        # old_tendency_data = [
        #     [0,1,0,0,1,0,0],
        #     [0,1,0,0,1,1],
        #     [0,0,0,1,0,0,1,0,0],
        #     [0,0,0,0,1,0,0,1],
        #     [1,0,0,0]
        # ]
        # 새로운 데이터 틀
        new_tendency_data = [
            old_tendency_data[0].copy(),
            old_tendency_data[1].copy(),
            [0,0,0,0,0,0], # 바뀔 부분
            [0,0,0,0,0,0,0,0,0,0,0], # 바뀔 부분
            old_tendency_data[4].copy(),
        ]
        
        # new_tendency_data[2] 매칭
        new_tendency_data[2][0] = old_tendency_data[2][0]  # 레저 스포츠
        new_tendency_data[2][1] = old_tendency_data[3][3]  # 산책
        new_tendency_data[2][2] = old_tendency_data[3][2]  # 드라이브
        new_tendency_data[2][3] = old_tendency_data[2][3]  # 이색체험
        new_tendency_data[2][4] = old_tendency_data[3][4]  # 쇼핑
        new_tendency_data[2][5] = old_tendency_data[3][6]  # 시티투어

        # new_tendency_data[3] 매칭
        new_tendency_data[3][0] = old_tendency_data[3][0]  # 바다
        new_tendency_data[3][1] = old_tendency_data[3][1]  # 산
        new_tendency_data[3][2] = old_tendency_data[3][5]  # 실내여행지
        new_tendency_data[3][3] = old_tendency_data[2][1]  # 문화시설
        new_tendency_data[3][4] = old_tendency_data[2][2]  # 사진 명소
        new_tendency_data[3][5] = old_tendency_data[2][4]  # 유적지
        new_tendency_data[3][6] = old_tendency_data[2][5]  # 박물관
        new_tendency_data[3][7] = old_tendency_data[3][7]  # 전통
        new_tendency_data[3][8] = old_tendency_data[2][6]  # 공원
        new_tendency_data[3][9] = old_tendency_data[2][7]  # 사찰
        new_tendency_data[3][10] = old_tendency_data[2][8]  # 성지

        return new_tendency_data

    except Exception as e:
        logger.error(f"Error in remakeTendency: {str(e)}")
        logger.error(old_tendency_data)
        logger.error(traceback.format_exc())
        return old_tendency_data
