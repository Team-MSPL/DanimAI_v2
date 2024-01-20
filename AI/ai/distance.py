import numpy as np
import math
from python_tsp.heuristics import solve_tsp_local_search

def tsp(path):
    l = len(path)
    distance_matrix = [[0 for _ in path] for _ in path]
    for i in range(l):
        for j in range(l):
            lat_diff = path[i]["latitude"] - path[j]["latitude"]
            lon_diff = path[i]["longitude"] - path[j]["longitude"]
            distance_matrix[i][j] = math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    distance_matrix = np.array(distance_matrix)
    permutation, distance = solve_tsp_local_search(distance_matrix)
    start = permutation[0]
    end = permutation[-1]
    lat_diff = path[start]["latitude"] - path[end]["latitude"]
    lon_diff = path[start]["longitude"] - path[end]["longitude"]
    distance -= math.sqrt((lat_diff ** 2) + (lon_diff ** 2))
    ts_path = [path[i] for i in permutation]
    return ts_path, distance