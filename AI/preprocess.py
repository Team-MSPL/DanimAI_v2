from .common.constant import Dummy


def preprocess(place_list, ex_essential_list, ex_accomodation_list):
    essential_list = essential_place_list_adaptor(ex_essential_list)
    accomodation_list = accomodation_list_adaptor(ex_accomodation_list)
    place_list = remove_duplicates(place_list, essential_list + accomodation_list)
    return place_list, essential_list, accomodation_list

def compare(place1, place2): # 다른 장소면  return true - 240122 위도, 경도 중 하나는 같을 수 있으니 or 연산으로 변경
    return abs(place1["latitude"] - place2["latitude"]) >= 0.002 or abs(place1["longitude"] - place2["longitude"]) >= 0.002
def remove_duplicates(place_list, ex_list):
    new_place_list = []
    for idx, place in place_list.items():
        flag = True
        for ex in ex_list:
            if not compare(place, ex):
                flag = False
        if flag:
            new_place_list.append(place)
    return new_place_list

def essential_place_list_adaptor(external_place_list):
    adapted_list = []
    for item in external_place_list:
        adapted_list.append({
            "name": item["name"],
            "latitude": item["lat"],
            "longitude": item["lng"],
            "taken_time": item["takenTime"],
            "popular": 0,
            "partner": Dummy.PARTNER,
            "concept": Dummy.CONCEPT,
            "play": Dummy.PLAY,
            "tour": Dummy.TOUR,
            "season": Dummy.SEASON,
            "category": item["category"],
            "photo": "",
            "day": item["day"],
            "is_essential": True,
            "is_dummy": False
        })
    return adapted_list

def accomodation_list_adaptor(external_place_list):
    adapted_list = []
    for item in external_place_list:
        adapted_list.append({
            "name": item.name,
            "latitude": item.lat,
            "longitude": item.lng,
            "takenTime": item.takenTime,
            "popular": 0,
            "partner": Dummy.PARTNER,
            "concept": Dummy.CONCEPT,
            "play": Dummy.PLAY,
            "tour": Dummy.TOUR,
            "season": Dummy.SEASON,
            "category": item.category,
            "photo": "",
            "is_essential": True,
            "is_dummy": True if item.name == "" else False
        })
    return adapted_list
