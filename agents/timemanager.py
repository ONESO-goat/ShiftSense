import asyncio
from services.worker_services import WorkerServices
from typing import Any, TYPE_CHECKING
from datetime import datetime
import time
from helpers.config import Config
from fastapi_config import get_session
from  sqlmodel import Session

worker_service = WorkerServices()


class TimeManager:
    def __init__(self, store):
        self.store = store
        self.ended_shift:dict[str, dict[str, Any]] = {}
        """
        [ "the_workers_id": {dict of their info}, ... ]
        """
        self._set_up_config_location()
        
    def check(self, session: Session):
        err = {
            "shifts": self.ended_shift,
            "content": "Either no workers or no ended shift at the current moment.",
            
        }
        current_hour = (datetime.now().hour + 1) % 24
        current_day = datetime.now().strftime("%A").lower()
        workers = worker_service.get_all_workers(session, store=self.store)
        if not workers:
            return err
        for worker in workers:
            worker_schedule = worker.schedule
            if not worker_schedule:
                continue
            
            day_schedule = worker_schedule.get(current_day)
            if not day_schedule or day_schedule.get('is_off', False) == True:
                continue 
            
            if day_schedule['shift_end'] == current_hour and worker.id not in self.ended_shift:
                self.ended_shift[str(worker.id)] = worker.model_dump()
        
        if not self.ended_shift:
            return err
        
        context = '' 
        for worker_id, worker_info in self.ended_shift.items():
            
            context += f"""
            \n
            {worker_info['name']}
            
            """
        return {
            "shifts": self.ended_shift,
            "content": context.lower().strip()
            }

    def get_ended_shift(self):
        return self.ended_shift
    
    def remove_worker_from_ended_shift(self, worker_id:int):
        self.ended_shift.pop(str(worker_id), None)
            
    async def hourly_check_loop(self):
        while True:
            with next(get_session()) as session: 
                self.check(session)
            
            await asyncio.sleep(3600)
            
    def _set_up_config_location(self):
        Config().change_location(new_location=self.store.city)