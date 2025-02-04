from typing import List, Optional
from fastapi import FastAPI
from fastapi import Response
from pydantic import BaseModel
import time
import os
#import traceback
import asyncio
from dotenv import load_dotenv
from AI.AI_service import request_handler, recommend_handler
from .firebase.firebaseAccess import FirebaseAccess
from concurrent.futures import ProcessPoolExecutor
from .logging_config import logger

# 숙소 및 필수여행지 input값을 추가하고자 할 때 여기 수정
class AccomodationListItem(BaseModel):
    name: str
    lat: float
    lng: float
    takenTime: int
    category: int
    regionIndex: Optional[int] = None  # regionIndex는 선택적인 값으로 설정
    id: Optional[str] = None
    photo: Optional[str] = None  # photo는 선택적인 값으로 설정
    formatted_address: Optional[str] = None
    region: Optional[str] = None

class EssentialPlaceListItem(BaseModel):
    day: int
    name: str
    lat: float
    lng: float
    category: int
    takenTime: int
    id: Optional[str] = None
    regionIndex: Optional[int] = None  # regionIndex는 선택적인 값으로 설정
    photo: Optional[str] = None  # photo는 선택적인 값으로 설정
    formatted_address: Optional[str] = None
    region: Optional[str] = None

class AIModel(BaseModel):
    regionList: List[str]
    accomodationList: List[AccomodationListItem]
    selectList: List[List[int]]
    essentialPlaceList: List[EssentialPlaceListItem]
    timeLimitArray: List[int]
    nDay: int
    transit: int
    distanceSensitivity: int
    bandwidth: bool
    password: str
    

class RecommendPlaceModel(BaseModel):
    regionList: List[str]
    selectList: List[List[int]]
    transit: int
    distanceSensitivity: int
    lat: float
    lng: float
    bandwidth: bool
    password: str
    

# async def run_blocking_io_function(args):
#     # ProcessPoolExecutor를 사용하여 I/O 작업을 실행
#     loop = asyncio.get_event_loop()
#     with ProcessPoolExecutor() as executor:
#         result = await loop.run_in_executor(executor, blocking_io_function, args)
#     return result


# def blocking_io_function(args):
#     # I/O 작업 수행
#     # 이곳에 CPU-bound 작업이나 시간이 오래 걸리는 작업을 넣으세요.
#     place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth = args
    
#     resultData, bestPointList, enough_place =  asyncio.run(request_handler(place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth))
    
#     return resultData, bestPointList, enough_place

print("연결 성공")
app = FastAPI()

# 요청 타임아웃 설정 (20초) - 없어도 20초는 괜찮은거 테스트해봄
#app.add_middleware(TimeoutMiddleware, timeout=20)

# 서버 시작 시 환경 변수를 한 번만 로드
load_dotenv()

logger.info("연결 성공")

@app.post("/ai/run")
async def ai_run(aiModel : AIModel):
    logger.info("API 호출 성공")
    #logger.error('Watch out!')  # will print a message to the console
    # logger.info('I told you so')  # will not print anything
        
    ai_key_list = os.getenv('AI_KEY').split(',')
    
    if aiModel.password not in ai_key_list: 
        return {"status" : "failed",
                "message": 'password error'
        }
    

    start = time.time()
    region_list = aiModel.regionList
    accomodation_list = aiModel.accomodationList
    select_list = aiModel.selectList
    essenstial_place_list = aiModel.essentialPlaceList
    time_limit_array = aiModel.timeLimitArray
    n_day = aiModel.nDay
    transit = aiModel.transit
    distance_sensitivity = aiModel.distanceSensitivity
    bandwidth = aiModel.bandwidth
    
    
    
    # FirebaseAccess.read_all_place가 동기적이면 비동기로 변경해야 함
    logger.info(f"API 호출 지역 - {region_list}")
    fb = FirebaseAccess()
    place_map, place_feature_matrix = await fb.read_all_place(region_list, select_list, bandwidth)
    
    
    # # blocking I/O 작업을 실행
    # args = (place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth)
    # resultData, bestPointList, enough_place = await run_blocking_io_function(args)  # 비동기로 실행

    # request_handler가 비동기 처리되도록 함
    resultData, bestPointList, enough_place = await request_handler(
        place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list,
        time_limit_array, n_day, transit, distance_sensitivity, bandwidth
    )

    end = time.time()
    logger.info(end - start)
    if len(resultData) == 0: 
        return {"status" : "failed",
                "message": '코스 제작 중 에러 발생'
        }
    return {
        "resultData" : resultData,
        "enoughPlace" : enough_place,
        "bestPointList" : bestPointList
        
    }
    
    
@app.post("/ai/recommendPlace")
async def recommend_place(model: RecommendPlaceModel):
    logger.info("Recommend Place API 호출 성공")
    ai_key_list = os.getenv('AI_KEY').split(',')

    # 비밀번호 유효성 검사
    if model.password not in ai_key_list:
        return {"status": "failed", "message": 'password error'}

    start = time.time()  # 실행 시작 시간 기록
    
    region_list = model.regionList
    select_list = model.selectList
    transit = model.transit
    distance_sensitivity = model.distanceSensitivity
    bandwidth = model.bandwidth
    lat = model.lat
    lng = model.lng

    # Firebase에서 장소 정보 읽기
    logger.info(f"Recommend Place API 호출 지역 - {region_list}")
    fb = FirebaseAccess()
    place_map, place_feature_matrix = await fb.read_all_place(region_list, select_list, bandwidth)
    
    place_list = list(place_map.values())

    # recommend_handler 호출하여 추천 결과 생성
    recommended_places = await recommend_handler(place_list, place_feature_matrix, select_list, transit, distance_sensitivity, lat, lng)

    end = time.time()  # 실행 종료 시간 기록
    logger.info(end - start)

    # 추천 장소가 없을 경우 실패 응답 반환
    if len(recommended_places) == 0:
        return {"status": "failed", "message": '추천 장소가 없습니다.'}

    # 성공 응답 반환
    return {
        "status": "success",
        "recommendedPlaces": recommended_places
    }