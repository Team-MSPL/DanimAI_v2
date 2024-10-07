from typing import List, Optional
from fastapi import FastAPI
from fastapi import Response
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv
from AI.AI_service import request_handler


# 숙소 및 필수여행지 input값을 추가하고자 할 때 여기 수정
class AccomodationListItem(BaseModel):
    name: str
    lat: float
    lng: float
    takenTime: int
    category: int
    regionIndex: Optional[int] = None  # regionIndex는 선택적인 값으로 설정

class EssentialPlaceListItem(BaseModel):
    day: int
    name: str
    lat: float
    lng: float
    category: int
    takenTime: int
    id: int
    regionIndex: Optional[int] = None  # regionIndex는 선택적인 값으로 설정

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

print("연결 성공")
app = FastAPI()

@app.post("/ai/run")
async def ai_run(aiModel : AIModel):
    print("API 호출 성공")
    
    load_dotenv()
        
    ai_key_list = os.getenv('AI_KEY').split(',')
    
    if aiModel.password not in ai_key_list: 
        return {"status" : "failed",
                "message": 'password error'
        }
        

    try:
        start = time.time()
        region_list = aiModel.regionList
        accomodation_list = aiModel.accomodationList
        select_list = aiModel.selectList
        essenstial_place_list = aiModel.essentialPlaceList
        time_limit_array = aiModel.timeLimitArray
        n_day = aiModel.nDay
        transit = aiModel.transit
        distance_sensitivity = aiModel.distanceSensitivity
        bandwitdth = aiModel.bandwidth

        resultData, bestPointList, enough_place = request_handler(region_list, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day,
                            transit, distance_sensitivity, bandwitdth)

        end = time.time()
        print(end - start)
        return {
            "resultData" : resultData,
            "enoughPlace" : enough_place,
            "bestPointList" : bestPointList
            
        }
    except:
        return {"status" : "failed",
                "message": 'Internal server error'
        }

