import copy
import traceback
from .common.constant import RESULT_NUM
from .logging_config import logger

# 2차원 배열을 원소별로 합하는 함수
def sum_2d_arrays(arr1, arr2):
    result = []
    for row1, row2 in zip(arr1, arr2):
        # 각 행의 같은 인덱스에 있는 값끼리 합산
        result.append([x + y for x, y in zip(row1, row2)])
    return result

# 2차원 배열을 원소별로 곱하는 함수
def multiply_2d_arrays(arr1, arr2):
    result = []
    for row1, row2 in zip(arr1, arr2):
        # 각 행의 같은 인덱스에 있는 값끼리 곱셈
        result.append([x * y for x, y in zip(row1, row2)])
    return result

def tendencyCalculate(path_list, select_list):
    tendencyAvg = [
            [0, 0, 0, 0, 0, 0, 0], #반려동물과는 나오면 안됨 - 250204 수정
            [0, 0, 0, 0, 0, 0], #
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0], #실내여행지는 나오면 안됨 - 250204 수정
            [0, 0, 0, 0],  #계절 점수는 지양 - 250204 수정
    ]
    tendencyData = [
            ['나홀로', '연인과', '친구와', '가족과', '효도', '자녀와', '반려동물과'],
            ['힐링', '활동적인', '배움이 있는', '맛있는', '교통이 편한', '알뜰한'],
            ['레저 스포츠', '문화시설', '사진 명소', '이색체험', '유적지', '박물관', '공원', '사찰', '성지'],
            ['바다', '산', '드라이브', '산책', '쇼핑', '실내여행지', '시티투어', '전통'],
            ['봄', '여름', '가을', '겨울'],
        ];
    
    best_point_list = []
    
    
    for path in path_list:
        placeNum = 0
        pathTendencyAvg = copy.deepcopy(tendencyAvg)
        
        for day_path in path:
            for place in day_path:
                
                if not place["is_essential"]:
                    placeNum += 1
                
                    concept_list = [place['partner'], place['concept'], place['play'], place['tour'], place['season']]
                    
                    # 계속 더해가며 업데이트
                    pathTendencyAvg = sum_2d_arrays(pathTendencyAvg, concept_list)
                    
        pathTendencyAvg = multiply_2d_arrays(pathTendencyAvg, select_list)
        
        if placeNum == 0:    # 전부 필수여행지랑 숙소인경우
            best_point_list.append({ "tendencyNameList": [], "tendencyPointList": [], "tendencyRanking": []})           
        
        pathTendencyAvg = [[x // placeNum for x in row] for row in pathTendencyAvg]
        
        tendencyPointList = []
        tendencyNameList = []

        for i, tendency in enumerate(pathTendencyAvg):
            for j,  score in enumerate(tendency):
                if score > 0:
                    if select_list[i][j] > 0 and i == 4:
                        tendencyPointList.append(score - 20)    # 계절 값만 -20 해주자
                        tendencyNameList.append(tendencyData[i][j])
                    else:
                        tendencyPointList.append(score)
                        tendencyNameList.append(tendencyData[i][j])
                # elif select_list[i][j] > 0 and i != 4:
                #     # 20점 넣고 랭킹에 제대로 뜨게 하자 + 계절 제외
                #     tendencyPointList.append(20)
                #     tendencyNameList.append(tendencyData[i][j])
                    

        best_point_list.append({'tendencyNameList': tendencyNameList, 'tendencyPointList': tendencyPointList})

    return best_point_list

def standardize(best_point_list):
    # def calculate_correction(diff):
    #     return (diff // 10 - 2.5) * 10 if diff % 10 == 0 else (diff // 10 - 1.5) * 10

    # isEnough = [False] * RESULT_NUM
    try:
        max_tendency_point_list = [
            max(path['tendencyPointList']) if path['tendencyPointList'] else 0
            for path in best_point_list
        ]


        for idx, path in enumerate(best_point_list):
            # 80점 넘는 성향이 있어도 나머지 애들은 보정하게 수정 - 250204
            # isEnough[idx] = any(tendencyPoint >= 80 for tendencyPoint in path['tendencyPointList'])
            
            max_tendency_point = max_tendency_point_list[idx]
            
            diff = 80 - max_tendency_point
            if diff < 0:
                return 0          
            
            for idx2, tendency_point in enumerate(path['tendencyPointList']):
                # 20점 이하이면 standardize X, 위에 20점 넣은 애들도 걸러지게
                if path['tendencyPointList'][idx2] <= 20:
                    continue
                
                if tendency_point == max_tendency_point:  # 보정 전 먼저 체크해야함
                    best_point_list[idx]['tendencyPointList'][idx2] += (diff // 10) * 10
                    
                else:
                    # 차이를 줄이기 위한 비율 계산 - 50% 차이를 줄이도록 설정
                    best_point_list[idx]['tendencyPointList'][idx2] += int((max_tendency_point - tendency_point) * 0.5)
                    
                    # 차이 보정 이후에 80점과 보정 작업
                    best_point_list[idx]['tendencyPointList'][idx2] += (diff // 10) * 10
                
    except Exception as error:
        logger.error(f"standardize 중에 에러 발생 :, {error}")  
        return best_point_list
        
    return best_point_list

def getRanking(best_point_list):
    for i in range(len(best_point_list[0]['tendencyPointList'])):
        
        # 각 i번째 요소에 대해 비어있지 않은 경우만 포함하는 rankList 생성 - 
        # 성향 선택 없이 계절 값만 넣었는데, 코스 내에 계절 점수가 40점 이상인게 1개도 없을 경우
        rankList = sorted(
            [path for path in best_point_list if i < len(path['tendencyPointList']) and path['tendencyPointList'][i] is not None and len(path['tendencyPointList'][i]) > 1],
            key=lambda x: x['tendencyPointList'][i],
            reverse=True
        )
        
        # rankList를 정렬한 순서대로 인덱스를 부여
        for j, path in enumerate(best_point_list):
            if 'tendencyRanking' not in path:
                best_point_list[j]['tendencyRanking'] = []
            
            # 현재 path의 i번째 값이 존재하면 랭킹을 계산하여 추가
            if i < len(path['tendencyPointList']) and path['tendencyPointList'][i] is not None and len(path['tendencyPointList'][i]) > 1:
                ranking = next(idx + 1 for idx, item in enumerate(rankList) if item == path)
                best_point_list[j]['tendencyRanking'].append(ranking)
                
    # # 랭킹 다 매기고, 20점 짜리 애들 삭제
    # for i, path in enumerate(best_point_list):
    #     for j in range(len(best_point_list[i]['tendencyPointList'])):
    #         if best_point_list[i]['tendencyPointList'][j] == 20:
    #             del best_point_list[i]['tendencyNameList'][j]
    #             del best_point_list[i]['tendencyPointList'][j]
    #             del best_point_list[i]['tendencyRanking'][j]

    return best_point_list


