
regionList = [
    "서울 동남권", "서울 서북권"
],  #x
accomodationList = [
    {
        "name": "",
        "lat": 35.333,
        "lng": 122.32323,
        "takenTime": 30,
        "category": 4
    },
    {
        "name": "",
        "lat": 35.333,
        "lng": 122.32323,
        "takenTime": 30,
        "category": 4
    },
    {
        "name": "",
        "lat": 35.333,
        "lng": 122.32323,
        "takenTime": 30,
        "category": 4
    },
    {
        "name": "",
        "lat": 34.333,
        "lng": 121.32323,
        "takenTime": 30,
        "category": 4
    },
    {
        "name": "",
        "lat": 34.333,
        "lng": 121.32323,
        "takenTime": 30,
        "category": 4
    }
], #  숙소 리스트. 숙소 미리 정해져있는 경우
selectList = [
    [
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ],
    [
        0,
        1,
        0,
        0,
        1,
        1
    ],
    [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ],
    [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ],
    [
        1,
        0,
        0,
        0
    ]
], # 성향 리스트, 선택했으면 1, 안했으면 0
essentialPlaceList = [
     {
       "day": 1,
       "name": "필수여행지1",
       "lat": 35.51243,
       "lng": 127.5436,
      "category": 5,
      "takenTime": 60,
       "id": 1
     },
     {
       "day": 2,
       "name": "필수여행지2",
       "lat": 35.12221,
      "lng": 127.6234,
       "category": 5,
       "takenTime": 60,
       "id": 1
     },
],  #필수 방문 리스트
timeLimitArray = [
    8,
    20
],  # 최대 시간
nDay = 4, # 며칠 여행인지
transit = 1,  # 0: 자차, 1: 대중교통
distanceSensitivity = 4, # 거리민감도
bandwidth= True  # 바쁜일정, 여유있는 일젖ㅇ