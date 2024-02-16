from typing import List
from fastapi import FastAPI
from fastapi import Response
from pydantic import BaseModel

from AI.AI_service import request_handler


class AccomodationListItem(BaseModel):
    name: str
    lat: float
    lng: float
    takenTime: int
    category: int


class EssentialPlaceListItem(BaseModel):
    day: int
    name: str
    lat: float
    lng: float
    category: int
    takenTime: int
    id: int


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

print("연결 성공")
app = FastAPI()

@app.post("/ai/run")
async def ai_run(aiModel : AIModel):
    print("API 호출 성공")
    region_list = aiModel.regionList
    accomodation_list = aiModel.accomodationList
    select_list = aiModel.selectList
    essenstial_place_list = aiModel.essentialPlaceList
    time_limit_array = aiModel.timeLimitArray
    n_day = aiModel.nDay
    transit = aiModel.transit
    distance_sensitivity = aiModel.distanceSensitivity
    bandwitdth = aiModel.bandwidth

    path = request_handler(region_list, accomodation_list, select_list, essenstial_place_list, time_limit_array, n_day,
                           transit, distance_sensitivity, bandwitdth)
    return { "resultData":path, "enoughPlace":True,"bestPointList":[] } #TODO 1) enoughPlace 처리 2) bestPointList 처리 3) try-execpt 해두기
    #return Response(path)