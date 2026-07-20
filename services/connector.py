from sqlmodel import Session
import random
from models import Store
from agents import shiftmanager, timemanager  # Your existing logic class
from typing import TYPE_CHECKING
from .worker_services import WorkerServices
from voicebox import listen, speak

ErrorOccuredBool = bool

class Connector:
    def __init__(self,
                 store:Store
                 ) -> None:
        
        self.store = store
        self.timemanager = self._setup_and_edit_timemanager(self.store)
        self.agent_runner = shiftmanager.Stora(store=self.store, timemanager=self.timemanager)
        self.voicebox = speak.Voice()
        self.ears = listen.Ears()
        
    def process(self, session):
        history = []
        while True:
            action = self.listen(session)
            data = self.respond(user_text=action, session=session)
            history.append(data)
            continue
        
    def respond(self,

                user_text:str,
                session:Session):
        if not user_text or not self.store:
            return ""
  
        action = self.agent_runner.listen_to_user(user_text)
        if not action:
            return f"Sorry, I don't know what '{action}' is. I can do reviews, hourly checks, check for ended shifts, just give me the word!"
        
        data = self.agent_runner.run_action(session=session,
                                            action=action, 
                                            workers=WorkerServices()
                                            .get_workers_working(session,store=self.store))
        if not data:
            return ""
        
        speech_response = data['content']
        self.voicebox.say(speech_response)
        return data
    
    def listen(self,     session: Session):

        while True:
            if self.ears.wait_for_wake_word():
                break
        att = 0
        self.voicebox.say(random.choice(['yes?', 
                                    "i'm all ears", 
                                    'listening', 
                                    'yours truly', 
                                    "Yes human",
                                    "what is it now"]))
        while True:
            if att >= 3:
                return ""
            
            action = self.ears.sr_listen()
            if not action:
                self.voicebox.say(random.choice(["I didn't quite catch that, can you please repeat", 
                                            "My apologies, I didnt catch that", 
                                            "please repeat that",
                                            "huh?"]))
                att += 1
                continue
            return action
    def greet(self):
        try:
            self.voicebox.say(f"Hey, I am Stora. Your most helpful manager for {self.store.name}. I am delighted to work with all the great humans!")
            return True
        except Exception as ex:
            print(f"ERROR DURING GREET: \n\t\u2022 {ex}")
            return False
    def review(self, session:Session)->tuple[ErrorOccuredBool,dict]:
  
        workers = WorkerServices().get_workers_working(session, store=self.store)
        info = self.agent_runner.review(workers)
        if info['error'].strip() != "":
            return True, info
        return False, info
    
    def obtain_ended_shift(self, session:Session)->tuple[ErrorOccuredBool, dict]:
        data = self.timemanager.check(session=session)
        if data['error'].strip() != "":
            return True, data
        return False, data
    
    def _setup_and_edit_timemanager(self, store):
        return timemanager.TimeManager(store=store)
