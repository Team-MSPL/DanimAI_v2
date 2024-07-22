import copy
def tendencyCalculate(path, themeList):
    tendencyAvg = [
            [0, 0, 0, 0, 0, 0, -1000], #반려동물과는 나오면 안됨
            [0, 0, 0, 0, 0, 0], #
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, -1000, 0, 0], #실내여행지는 나오면 안됨
            [-100, -100, -100, -100],  #계절 점수는 지양
    ]
    tendencyData = [
            ['나홀로', '연인과', '친구와', '가족과', '효도', '자녀와', '반려동물과'],
            ['힐링', '액티비티', '배움이 있는', '맛있는', '교통이 편한', '알뜰한'],
            ['레저 스포츠', '문화시설', '사진 명소', '이색체험', '유적지', '박물관', '공원', '사찰', '성지'],
            ['바다', '산', '드라이브', '산책', '쇼핑', '실내여행지', '시티투어', '전통한옥'],
            ['봄', '여름', '가을', '겨울'],
        ];

    dayList = []

    placeNum = 0
    for day_path in path:
        for places in day_path:
            for place in places:
                placeNum += 1
                concept_list = [place['partner'], place['concept'], place['play'], place['tour'], place['season']]
                for conceptIdx, concept in enumerate(concept_list):
                    indexList = copy.deepcopy(tendencyAvg[conceptIdx])
                    for i ,score in enumerate(concept):
                        indexList[i] += score
                        if day_path == path[-1] and place == day_path[-1]:
                            indexList[i] = (indexList[i] // placeNum) * themeList[conceptIdx][i]
                    tendencyAvg[conceptIdx] = indexList

        tendencyPointList = [];
        tendencyNameList = [];

        for i, tendency in enumerate(tendencyAvg):
            for j,  score in enumerate(tendency):
                if score > 0:
                    tendencyPointList.append(score)
                    tendencyNameList.append(tendencyData[i][j])

        dayList.append({'tendencyNameList': tendencyNameList, 'tendencyPointList': tendencyPointList})

    return dayList

def standardize(pathsThemeList):

    themeNum = len(pathsThemeList[0]['tendencyPointList'])
    isEnough = False;

    for i in range(themeNum):
        for path in pathsThemeList:
            if path['tendencyPointList'][i] > 80:
                isEnough = True;

        if not isEnough:
            for _, path in enumerate(pathsThemeList):
                diff = 100 - path['tendencyPointList'][i]
                correction = (diff // 10 - 2.5) * 10 if diff % 10 == 0 else (diff // 10 - 1.5) * 10;
                path['tendencyPointList'][i] += correction;
                if correction > 40:
                    path['tendencyPointList'][i] -= 10;

    return pathsThemeList

def getRanking(pathThemeList):
    for i in range(len(pathThemeList[0]['tendencyPointList'])):
        rankList = sorted(pathThemeList, key=lambda x: x['tendencyPointList'][i])
        rankList = [x['tendencyPointList'][i] for x in rankList]
        for j, path in enumerate(pathThemeList):
            if 'tendencyRanking' not in path:
                pathThemeList[j]['tendencyRanking'] = []
            pathThemeList[j]['tendencyRanking'].append(rankList.index(path['tendencyPointList'][i]) + 1)

    return pathThemeList

