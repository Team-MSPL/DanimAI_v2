import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import numpy as np

from google.cloud.firestore_v1 import FieldFilter


def read_all_place(region, bandwidth):
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
    cred = credentials.Certificate("/Users/mihnhyuk/PycharmProjects/DanimAI_v2/private_key/danim-3439e-firebase-adminsdk-9ud51-36d28c31ba.json")  # Firebase Admin SDK 인증 정보
    firebase_admin.initialize_app(cred, firebase_config)

    db = firestore.client()  # 파이어스토어 접근

    all_place_map = {}
    place_feature = []
    try:
        idx = 0
        for r in region:
            # "관광지 목록" 문서는 제외
            place_snapshot = db.collection(r).where(filter=FieldFilter("name", "!=", '관광지목록')).get()
            for _, place in enumerate(place_snapshot):
                # data.append(place.to_dict())
                data = place.to_dict()
                if bandwidth:
                    data["takenTime"] += 30
                place = {
                    "name": data["name"],
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "popular" : data["popular"],
                    "taken_time": data["takenTime"],
                    "partner": data["partner"],
                    "concept": data["concept"],
                    "play": data["play"],
                    "tour": data["tour"],
                    "season": data["season"],
                    "category": 0,
                    "photo": data["photo"],
                    "is_essential": False,
                    "is_dummy": False
                }
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
                    place_feature = np.append(place_feature, feature, axis=0)
    except Exception as error:
        print("관광지 데이터셋을 읽어오는 중에 오류가 발생했습니다:", error)

    return all_place_map, place_feature