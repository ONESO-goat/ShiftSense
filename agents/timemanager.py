import asyncio
from services.worker_services import WorkerServices
from typing import TYPE_CHECKING
from datetime import datetime
import time
from stora.helpers.config import Config
from fastapi_config import get_session
from  sqlmodel import Session
if TYPE_CHECKING:
    from engine import Engine

worker_service = WorkerServices()


class TimeManager:
    def __init__(self,  
                api_key:str|None=Config.gemini_api_key,
                ai_to_use:str="ollama"):
        
        self.engine = Engine(api_key=api_key, ai_to_use=ai_to_use)
        self.ended_shift = {}
        
    def check(self, session: Session):
        current_hour = (datetime.now().hour + 1) % 24
        current_day = datetime.now().strftime("%A").lower()
        workers = worker_service.get_all_workers(session)
        
        for worker in workers:
            worker_schedule = worker.schedule
            if not worker_schedule:
                continue
            
            day_schedule = worker_schedule.get(current_day)
            if not day_schedule or day_schedule.is_off:
                continue 
            
            if day_schedule.shift_end == current_hour and worker.id not in self.ended_shift:
                self.ended_shift[worker.id] = worker

    def get_ended_shift(self):
        return self.ended_shift
    
    def remove_worker_from_ended_shift(self, worker_id:int):
        self.ended_shift.pop(worker_id, None)
            
    async def hourly_check_loop(self):
        while True:
            with next(get_session()) as session: 
                self.check(session)
            
            await asyncio.sleep(3600)