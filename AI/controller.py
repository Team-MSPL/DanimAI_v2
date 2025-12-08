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
from .remake_tendency import remakeTendency
from .ai.BO.optimize_weights import optimize_weights

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
    popularSensitivity: int = 5  # 기본값 설정
    bandwidth: bool
    password: str
    version: int = 1  # 기본값 설정
    

class RecommendPlaceModel(BaseModel):
    regionList: List[str]
    selectList: List[List[int]]
    transit: int
    distanceSensitivity: int
    popularSensitivity: int = 5  # 기본값 설정
    lat: float
    lng: float
    bandwidth: bool
    password: str
    version: int = 1  # 기본값 설정
    page: int = 1  # 기본값 설정
    page_for_place: int = 10  # 기본값 설정
    

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
    popular_sensitivity = aiModel.popularSensitivity
    bandwidth = aiModel.bandwidth
    version = aiModel.version
    
    # 어차피 프론트엔드에서 새로운 배열로 줄 것임
    # if version == 3:
    #     select_list = remakeTendency(select_list)
    
    # FirebaseAccess.read_all_place가 동기적이면 비동기로 변경해야 함
    logger.info(f"version - {version}")
    if region_list == ['제주 전체']:
        region_list = ['제주 제주시', '제주 서귀포시']
    elif region_list == ['서울 전체']:
        region_list = ['서울 도심권', '서울 서북권', '서울 서남권', '서울 동북권', '서울 동남권']

    logger.info(f"API 호출 지역 - {region_list}")

    fb = FirebaseAccess()
    place_map, place_feature_matrix = await fb.read_all_place(region_list, select_list, bandwidth, version)
        
    user_context = {}
    
    user_context.update({
        "region": region_list,
        "select_list": select_list,
        "distance_sensitivity": distance_sensitivity,
        "popular_sensitivity": popular_sensitivity,
        "n_day": n_day,
        "transit": transit,
        "bandwidth": bandwidth,
        "enough_place": enough_place,
    })      
    
    # # blocking I/O 작업을 실행
    # args = (place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day, transit, distance_sensitivity, bandwidth)
    # resultData, bestPointList, enough_place = await run_blocking_io_function(args)  # 비동기로 실행

    # request_handler가 비동기 처리되도록 함
    resultData, bestPointList, enough_place, result_eval = await request_handler(
        place_map, place_feature_matrix, accomodation_list, select_list, essenstial_place_list,
        time_limit_array, n_day, transit, distance_sensitivity, popular_sensitivity, bandwidth, user_context, version
    )

    end = time.time()
    logger.info(end - start)
    if len(resultData) == 0: 
        return {"status" : "failed",
                "message": '코스 제작 중 에러 발생'
        }
        
    try:
        from filelock import FileLock
        import json     
        
        # 강화학습
        best_params = optimize_weights(result_eval, user_context)
        logger.info("best_params")
        logger.info(best_params)
        
        
        # 객체 합치기
        result_eval = result_eval | user_context

        def save_result_eval(result_eval, filepath="result_eval.json"):
            lock_path = filepath + ".lock"
            with FileLock(lock_path):
                with open(filepath, "a", encoding="utf-8") as f:
                    json.dump(result_eval, f, ensure_ascii=False)
                    f.write("\n")
                    
        save_result_eval(result_eval, filepath="/home/ubuntu/result_eval.json")
        
    except Exception as e:
        logger.error("평가 함수 저장 중 에러 발생")
        logger.error(e)
    
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
    popular_sensitivity = model.popularSensitivity
    bandwidth = model.bandwidth
    lat = model.lat
    lng = model.lng
    version = model.version
    page = model.page
    page_for_place = model.page_for_place

    # 어차피 프론트엔드에서 새로운 배열로 줄 것임
    # if version == 3:
    #     select_list = remakeTendency(select_list)
    
    # Firebase에서 장소 정보 읽기
    logger.info(f"version - {version}")
    if region_list == ['제주 전체']:
        region_list = ['제주 제주시', '제주 서귀포시']
    elif region_list == ['서울 전체']:
        region_list = ['서울 도심권', '서울 서북권', '서울 서남권', '서울 동북권', '서울 동남권']

    logger.info(f"Recommend Place API 호출 지역 - {region_list}")
    fb = FirebaseAccess()
    place_map, place_feature_matrix = await fb.read_all_place(region_list, select_list, bandwidth, version)
    
    place_list = list(place_map.values())
    
    
    user_context = {}
    
    user_context.update({
        "region": region_list,
        "select_list": select_list,
        "distance_sensitivity": distance_sensitivity,
        "popular_sensitivity": popular_sensitivity,
        "n_day": 3, # TODO - 고정값, 필요시 수정
        "transit": transit,
        "bandwidth": bandwidth,
    })      
    

    # recommend_handler 호출하여 추천 결과 생성
    recommended_places = await recommend_handler(place_list, place_feature_matrix, select_list, transit, distance_sensitivity, popular_sensitivity, lat, lng, version, page, page_for_place, user_context)

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