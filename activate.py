from sqlmodel import Session
from models import Store, StoreStora
from agents import shiftmanager, timemanager  # Your existing logic class

class setup:
    def run(self, session: Session, store_id: str, user_message: str):
        # 1. Grab the data from the DB
        store = session.get(Store, store_id)
        if not store:
            raise ValueError("Store not found")
            
        # 2. Spin up your pure Python execution class with the fresh DB data
        # (Assuming you pass your TimeManager context here)
        the_timemanager = self._setup_and_edit_timemanager(store)
        agent_runner = shiftmanager.Stora(store=store, timemanager=the_timemanager)
        
        # 3. Use your logic seamlessly
        action = agent_runner.listen_to_user(user_message)
        return action
    
    def _setup_and_edit_timemanager(self, store):
        return timemanager.TimeManager(store=store)
