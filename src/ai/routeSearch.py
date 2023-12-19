import numpy as np
from src.ai.place_score import get_place_score_list
def route_search(placeList,place_feature_matrix, accomodationList, theme_matrix, essentialPlaceList, timeLimit, nDay):
    selectedThemeNumList = np.count_nonzero(theme_matrix, axis=1)
    activatedThemeNum = np.count_nonzero(selectedThemeNumList)

    place_preference_score_list, distanceBias = get_place_score_list(place_feature_matrix, theme_matrix, selectedThemeNumList, activatedThemeNum)

    print(place_preference_score_list.shape, distanceBias)
    # print(place_preference_score_list)
    # print(distanceBias)
    # np.append(placeList, place_preference_score_list)
    # print(placeList)



# routerSearch(parameter.accomodationList, theme_matrix, parameter.essentialPlaceList, np.array(parameter.timeLimitArray), parameter.nDay)