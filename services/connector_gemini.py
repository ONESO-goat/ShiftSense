import asyncio
from sqlmodel import Session
import random
from models import Store
from agents import shiftmanager, timemanager
from .worker_services import WorkerServices

class GeminiStoraSession:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.timemanager = self._setup_and_edit_timemanager(self.store)
        self.agent_runner = shiftmanager.Stora(store=self.store, timemanager=self.timemanager)
        self.is_talking: bool = False
        
    # NOTE: The loop 'process' is removed here because it now lives 
    # directly inside the FastAPI WebSocket lifecycle loop.

    async def respond(self, user_text: str, session: Session) -> tuple[bool, dict | str]:
        if not user_text or not self.store:
            return False, ""
  
        # Run synchronous AI/parsing logic in a thread pool so it doesn't block the async loop
        action = await asyncio.to_thread(self.agent_runner.listen_to_user, user_text)
        
        if not action:
            msg = f"Sorry, I don't know what '{user_text}' implies. I can do reviews, hourly checks, check for ended shifts, just give me the word!"
            return False, msg
        
        workers = await asyncio.to_thread(WorkerServices().get_workers_working, session, store=self.store)
        
        data, mes = await asyncio.to_thread(
            self.agent_runner.run_action, 
            session=session, 
            action=action, 
            workers=workers
        )
        
        if not data:
            return False, mes
        
        return True, data

    def greet_text(self) -> str:
        return f"Hey, I am Stora. Your most helpful manager for {self.store.name}. I am delighted to work with all the great humans!"

    def _setup_and_edit_timemanager(self, store):
        return timemanager.TimeManager(store=store)
