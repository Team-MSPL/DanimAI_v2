from src.ai.routeSearch import route_search
from src.firebase.firebaseAccess import read_all_place


def request_handler(regionList, accomodationList, selectList, essentialPlaceList, timeLimitArray, nDay, transit, distanceSensitivity, bandwidth):

    place_list = read_all_place(regionList, bandwidth)
    route_search(place_list, accomodationList, selectList, timeLimitArray, nDay, transit)
