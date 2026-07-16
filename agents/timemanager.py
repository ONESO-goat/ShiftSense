import typing
from typing import TYPE_CHECKING
from datetime import time, datetime
from stora.helpers.config import Config
import time
if TYPE_CHECKING:
    from engine import Engine



class TimeManager:
    def __init__(self, 
                workers: list, 
                api_key:str|None=Config.gemini_api_key,
                ai_to_use:str="ollama"):
        
        self.engine = Engine(api_key=api_key, ai_to_use=ai_to_use)
        self.shift_workers = workers
        self.shift_is_over = []
        
    def check(self):
        current_hour = datetime.now().time
        current_day = datetime.now().strftime("%A").lower()
        
        for worker in self.shift_workers:
            worker_schedule = worker.get("schedule", None)
            if not worker_schedule:
                continue
            worker['']
            
            
    def test(self):
        