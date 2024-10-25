import copy
import traceback

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
            [0, 0, 0, 0, 0, 0, -1000], #반려동물과는 나오면 안됨
            [0, 0, 0, 0, 0, 0], #
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1000, 0, 0], #실내여행지는 나오면 안됨
            [-100, -100, -100, -100],  #계절 점수는 지양
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
        
        pathTendencyAvg = [[x // placeNum for x in row] for row in pathTendencyAvg]

        tendencyPointList = []
        tendencyNameList = []

        for i, tendency in enumerate(pathTendencyAvg):
            for j,  score in enumerate(tendency):
                if score > 0:
                    tendencyPointList.append(score)
                    tendencyNameList.append(tendencyData[i][j])

        best_point_list.append({'tendencyNameList': tendencyNameList, 'tendencyPointList': tendencyPointList})

    return best_point_list

def standardize(best_point_list):

    themeNum = len(best_point_list[0]['tendencyPointList'])
    isEnough = False

    for i in range(themeNum):
        for tendency in best_point_list:
            if tendency['tendencyPointList'][i] > 80:
                isEnough = True
                break

        if not isEnough:
            for _, path in enumerate(best_point_list):
                diff = 100 - path['tendencyPointList'][i]
                correction = (diff // 10 - 2.5) * 10 if diff % 10 == 0 else (diff // 10 - 1.5) * 10;
                path['tendencyPointList'][i] += correction
                if correction > 40:
                    path['tendencyPointList'][i] -= 10

    return best_point_list

def getRanking(best_point_list):
    for i in range(len(best_point_list[0]['tendencyPointList'])):
        # 각 i번째 요소에 대한 rankList 생성
        rankList = sorted(best_point_list, key=lambda x: x['tendencyPointList'][i], reverse=True)
        
        # rankList를 정렬한 순서대로 인덱스를 부여
        for j, path in enumerate(best_point_list):
            if 'tendencyRanking' not in path:
                best_point_list[j]['tendencyRanking'] = []
            
            # 현재 path의 i번째 값에 해당하는 랭킹을 계산하여 추가
            ranking = next(idx + 1 for idx, item in enumerate(rankList) if item == path)
            best_point_list[j]['tendencyRanking'].append(ranking)

    return best_point_list


