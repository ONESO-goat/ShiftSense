from .engine import Engine
from  helpers.prompts import Prompts
from .forecast import Forecast
from datetime import datetime
from services.store_services import StoreService
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Store
    from timemanager import TimeManager

class StoraCalls(Enum):
    NONE = ""
    REVIEW = "review"
    HOUR_CHECK = "hour_check"
    ENDED_SHIFTS = "ended_shift"
    TAKING_A_BREAK = "break"
    

class Stora:
    def __init__(self, store:'Store', timemanager:'TimeManager', forecast:'Forecast|None'=None):
        if not store:
            raise ValueError("A store is required, how will stora learn the franchise!")
        
        self.store:'Store' = store
        self.engine:'Engine' = Engine()
        self.timemanager:'TimeManager' = timemanager
        self._prompts: 'Prompts' = Prompts()
        if forecast is not None:
            self.forcast = forecast
        else:
            self.forecast = Forecast(self.store)

    def run_action(self, session, action:str, workers:list|None=None):
        if not action:
            return None

        actions = {
            StoraCalls.REVIEW.value: self.review,
            StoraCalls.ENDED_SHIFTS.value: self.timemanager.check,
            StoraCalls.HOUR_CHECK.value: self.timemanager.check,
            
        }
        if action not in actions:
            return None
        
        if action == StoraCalls.REVIEW.value and workers is not None:
            return actions[action](workers)
        return actions[action](session)

        
    def review(self, workers:list):
        """
        Review staffing amount

        Args:
            workers (list): The workers working today

        The agent return dict with status: ("overstaffed", "understaffed", or "sufficient") 
        and reason: The reason behind its choice,
            
        Returns:
            dict: dict with info including the;
            content: Agent summary
            error: An errors during the process
            
        """
        err = {
            "content": "",
            "error": ""
        }
        txt = self._today_workers_data_to_string(workers)
        if not txt:
            err['error'] += f"[TIER 1 ERROR] The _today_workers_data_to_string returned nothing inside `Stora.review()`: \n\t\u2022 {txt}"
            return err
        
        response = self.engine._genrate(text=txt, 
                                        system_prompt=self._prompts.agent_purpose,
                                        return_json=True)
        
        if not response:
            err['error'] += f"[TIER 5 ERROR] The agent returned no response inside `Stora.review()`: \n\t\u2022 {response}"
            return err

        if response['status'].lower().strip() == 'sufficient':
            err['content'] = "At the moment, we are sufficient in the amount of workers"
            return err
        
        err['content'] = "At the moment, we are sufficient in the amount of workers"
        return err
    
    
    def _is_request_relevant(self, user_text:str):
        response = self.engine._genrate(text=user_text, system_prompt=self._prompts.is_the_users_request_related_to_stora)
        if not response:
            raise ValueError(f"[TIER 5 ERROR] The agent returned no response inside `Stora.is_request_relevant()`: \n\t\u2022 {response}")

        return "true" in response.lower()
    
    def listen_to_user(self, text)->str:
        if not text:
            return ""
            
        if not self._is_request_relevant(text):
            return "Sorry, I can't fulfill that request as I am designed to handle store flow."
        
    
        if "review" in  text: # ex: "do a review", "review", "store, review" WRONG: "Can you do a review on the ended shift"
            return StoraCalls.REVIEW.value
            
        elif "hour check" in text:
            return StoraCalls.HOUR_CHECK.value
        
        elif all(word in text for word in ['shift', 'end']):
            return StoraCalls.ENDED_SHIFTS.value
        
        else:
            return StoraCalls.NONE.value
        
    def give_recommendations(self):
        pass
    
    
    def update_date(self):
        self.forcast.update_date()
    

    def _today_workers_data_to_string(self, workers_working_today:list['Worker']|None):
        if not workers_working_today:
            return ""
        
        result = f"AMOUNT: {len(workers_working_today)} workers trhoughout the day\n"
        
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
        
        
    
