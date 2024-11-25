import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import numpy as np
import copy
from ..logging_config import logger

from google.cloud.firestore_v1 import FieldFilter

class FirebaseAccess():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FirebaseAccess, cls).__new__(cls, *args, **kwargs)
            cls.make_connection(cls)

        return cls._instance
    def make_connection(self):
        load_dotenv()  # .env 파일의 환경 변수 로드
        firebase_config = {
            "apiKey": os.getenv("GOOGLE_API_KEY"),
            "authDomain": "danim-3439e.firebaseapp.com",
            "projectId": "danim-3439e",
            "storageBucket": "danim-3439e.appspot.com",
            "messagingSenderId": "70367155908",
            "appId": "1:70367155908:web:39c1344d65ecce16141b91",
            "measurementId": "G-VXZTLNFY84",
        }
        cred = credentials.Certificate(
            "/home/ubuntu/DanimAI_v2/private_key/danim-3439e-firebase-adminsdk-9ud51-b49b933f86.json")  # Firebase Admin SDK 인증 정보

        firebase_admin.initialize_app(cred, firebase_config)

        self.db = firestore.client()  # 파이어스토어 접근

    async def read_all_place(self, region, select_list, bandwidth):
        db = self.db
        all_place_map = {}
        place_feature = []
        try:
            idx = 0
            for r_index, r in enumerate(region):
                # "관광지 목록" 문서는 제외
                place_snapshot = db.collection(r).where(filter=FieldFilter("name", "!=", '관광지목록')).get()
                #place_snapshot = db.collection("해외").document("Vietnam").collection("닌빈").where(filter=FieldFilter("name", "!=", '관광지목록')).get()
                
                for _, place in enumerate(place_snapshot):
                    # data.append(place.to_dict())
                    data = place.to_dict()

                    #반려견과 선택시 placeList에서 먼저 제거 - 240123
                    if select_list[0][6] == 1 and data["partner"][6] == 0:
                        continue

                    #여유로운 여행이면 takenTime 30분 추가 - 240122
                    if bandwidth:
                        data["takenTime"] += 30

                    # 실내여행지 예외처리 - 관광지 점수가 40점 이하면 걍 -10000으로 바꿔서 잘 안뜨게 함
                    data["tour"][5] = -10000 if data["tour"][5] <= 40 else data["tour"][5]

                    # 계절도 예외처리 - 여긴 더 심하게 낮은 점수로
                    data["season"][:] = [-100000 if x <= 40 else x for x in data["season"]]
                    
                    place = {
                        "name": data["name"],
                        "lat": data["latitude"],
                        "lng": data["longitude"],
                        "takenTime": data["takenTime"],
                        "popular" : data["popular"],
                        "partner": data["partner"],
                        "concept": data["concept"],
                        "play": data["play"],
                        "tour": data["tour"],
                        "season": data["season"],
                        "category": 0,
                        "photo": data.get("photo", ""),  # photo가 없으면 빈 문자열을 기본값으로 설정
                        "regionIndex": r_index,
                        "is_essential": False,
                        "is_accomodation": False,
                        "is_dummy": False
                    }
                    
                    

                    # id 키가 있으면 제거
                    place.pop("id", None)  # 'None'은 'id'가 없을 경우 KeyError를 방지
                    
                    feature = np.array([[
                        data["partner"] + [0, 0],
                        data["concept"] + [0, 0, 0],
                        data["play"],
                        data["tour"] + [0],
                        data["season"] + [0, 0, 0, 0, 0]
                    ]], dtype=int)
                    all_place_map[idx] = place
                    idx += 1
                    # print(feature.shape)
                    if len(place_feature) == 0:
                        place_feature = feature
                    else:
                        place_feature = np.append(place_feature, feature, axis=0)    # Deep Copy가 된다는 사실 확인하였음
        except Exception as error:
            logger.info("관광지 데이터셋을 읽어오는 중에 오류가 발생했습니다:", error)

        return all_place_map, place_feature