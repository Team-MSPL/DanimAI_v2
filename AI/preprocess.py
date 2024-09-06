from .common.constant import Dummy


def preprocess(place_list, ex_essential_list, ex_accomodation_list):
    essential_list = essential_place_list_adaptor(ex_essential_list)
    accomodation_list = accomodation_list_adaptor(ex_accomodation_list)
    place_list = remove_duplicates(place_list, essential_list + accomodation_list)
    return place_list, essential_list, accomodation_list

def compare(place1, place2): # 다른 장소면  return true - 위도, 경도 중 하나는 같을 수 있으니 or 연산으로
    return abs(place1["lat"] - place2["lat"]) >= 0.002 or abs(place1["lng"] - place2["lng"]) >= 0.002

# 사용자가 넣은 숙소 및 필수여행지가 place_list에도 있는 것을 방지함
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

    default_values = {
        "popular": 0,
        "partner": Dummy.PARTNER,
        "concept": Dummy.CONCEPT,
        "play": Dummy.PLAY,
        "tour": Dummy.TOUR,
        "season": Dummy.SEASON,
        "photo": "",
        "is_essential": True,
        "is_accomodation" : False,
        "is_dummy": False
    }

    for item in external_place_list:
        # 객체의 모든 속성을 딕셔너리로 변환
        item_dict = item.__dict__

        # 두 딕셔너리 병합 (item_dict가 default_values의 값을 덮어씀) - 필수여행지 객체값을 그대로 복사해서 돌려주게 ( regionIndex 및 이후 추가될 가능성이 있는 요소들 )
        merged_dict = {**default_values, **item_dict}


        # id 키가 있으면 제거
        merged_dict.pop("id", None)  # 'None'은 'id'가 없을 경우 KeyError를 방지

        adapted_list.append(merged_dict)

    return adapted_list

def accomodation_list_adaptor(external_place_list):
    adapted_list = []

    default_values = {
        "popular": 0,
        "partner": Dummy.PARTNER,
        "concept": Dummy.CONCEPT,
        "play": Dummy.PLAY,
        "tour": Dummy.TOUR,
        "season": Dummy.SEASON,
        "photo": "",
        "is_essential": True,
        "is_accomodation": True
    }

    for item in external_place_list:
        # 객체의 모든 속성을 딕셔너리로 변환
        item_dict = item.__dict__

        # 두 딕셔너리 병합 (item_dict가 default_values의 값을 덮어씀) - 필수여행지 객체값을 그대로 복사해서 돌려주게 ( regionIndex 및 이후 추가될 가능성이 있는 요소들 )
        merged_dict = {**default_values, **item_dict}


        # id 키가 있으면 제거
        merged_dict.pop("id", None)  # 'None'은 'id'가 없을 경우 KeyError를 방지

        # "is_dummy" 추가 - 숙소 유무에 따라 다르게 해야하기 때문
        merged_dict["is_dummy"] = True if item.name == "" else False

        adapted_list.append(merged_dict)

    return adapted_list
