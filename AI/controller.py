from typing import List
from fastapi import FastAPI
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


app = FastAPI()

@app.post("/ai/run")
async def ai_run(aiModel : AIModel):
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
    return path