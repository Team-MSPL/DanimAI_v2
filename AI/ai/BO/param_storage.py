# param_storage.py
import os
import json

STORE_PATH = "./best_params.json"


def load_all_params():
    """전체 JSON을 로드"""
    if not os.path.exists(STORE_PATH):
        return {}
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_all_params(data):
    """전체 덮어쓰기 방식으로 저장"""
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_context_params(key):
    """특정 key의 weight & best_reward 불러오기"""
    all_data = load_all_params()
    return all_data.get(key, None)  # {params, best_reward} or None


def save_context_params(key, params, best_reward):
    """특정 key의 params, best_reward 저장"""
    all_data = load_all_params()
    all_data[key] = {
        "params": params,
        "best_reward": best_reward
    }
    save_all_params(all_data)
