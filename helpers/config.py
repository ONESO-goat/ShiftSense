import dotenv
import os
import json
from typing import Any
from enum import Enum


dotenv.load_dotenv()

    
class Config:
    gemini_api_key = os.getenv("GEMINI_API_KEY1")
    
    worker_file = "brain/workers.json"
    
    # Ollama config
    ollama_model_qwen = 'qwen3:0.6b'
    
    # Gemini config
    gemini_model = 'gemini-2.5-flash'
  
if not Config.gemini_api_key:
    raise ValueError("API key is NONE")

def _get_json(path:str)->Any:
    if not path:
        return
    
    with open(path, 'r') as file:
        return json.load(file)

def get_worker_database()->dict:
    return _get_json(Config.worker_file)

def save_new_worker(Id:str, worker_data:dict):
    file = get_worker_database()
    if not file:
        raise ValueError("DATABASE was not accessed")
    file[Id] = worker_data
    with open(Config.worker_file, 'w') as f:
        json.dump(file, f, indent=4)