from .engine import Engine
from  helpers.prompts import Prompts
from forecast import Forecast
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Store


class Stora:
    def __init__(self, store:'Store', forecast:'Forecast|None'=None):
        if not store:
            raise ValueError("A store is required, how will stora learn the franchise!")
        
        self.store:'Store' = store
        self.engine:'Engine' = Engine()
        self._prompts: 'Prompts' = Prompts()
        if forecast is not None:
            self.forcast = forecast
        else:
            self.forecast = Forecast(current_day=datetime.now().date().day)

        
        self.personailty:str = self._prompts.agent_purpose
        
    def give_recommendations(self):
        rec_prompt = self._prompts.give_recommendation
        self.engine._genrate()
        
    def update_date(self):
        self.forcast.update_date()
        
    def _today_workers_data_to_string(self, workers_working_today:list['Worker']|None):
        if not workers_working_today:
            return ""
        
        result = ""
        for idx, worker in enumerate(workers_working_today):
            workers_schedule = worker.schedule
            current_day = workers_schedule.get(self.forcast.current_weekday, "")
            
            result += f"""
            ================= WORKER {idx} =================
            
            * ID: {worker.id}
            * NAME: {worker.name}
            * DEPARTMENT: {worker.department}
            * PAY: {worker.pay} per hour
            * STARTS AT: HOUR {current_day['shift_start']}
            * ENDS AT: HOUR {current_day['shift_end']}
            
            ================================================\n
            
            
            """.strip()
            
        return result
            
        
    
    def change_store(self, new_store:'Store'):
        self.store = new_store
        
        
    
    