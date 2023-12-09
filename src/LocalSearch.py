import numpy as np
import constant
import parameter
import placeListBuilder

def routerSearch(accomodationList, themeList, essentialPlaceList, timeLimit, nDay):

    count = np.count_nonzero(themeList)
    placeList = placeListBuilder.placeListBuilder()
    todayEssentialPlaceList = []


selectList = parameter.selectList
themeList = np.array(selectList, dtype=object)

routerSearch(parameter.accomodationList, themeList, parameter.essentialPlaceList, np.array(parameter.timeLimitArray), parameter.nDay)