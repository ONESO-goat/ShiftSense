from sqlmodel import Session
import random
from models import Store
from agents import shiftmanager, timemanager  # Your existing logic class
from typing import TYPE_CHECKING
import time
from .worker_services import WorkerServices
from voicebox import listen, speak

ErrorOccuredBool = bool

class StoraSession:
    def __init__(self,
                 store:Store
                 ) -> None:
        
        self.store = store
        self.timemanager = self._setup_and_edit_timemanager(self.store)
        self.agent_runner = shiftmanager.Stora(store=self.store, timemanager=self.timemanager)
        self.voicebox = speak.Voice()
        self.ears = listen.Ears()
        self.is_talking:bool = False
        self.is_busy: bool = False
        
    def process(self, session):
        att:int = 0
        history = []
        hold:bool = True
        
        while True:
            # if self.is_talking:
            #     yield None
            #     continue
            time.sleep(0.1)
                
            if att >= 3:
                hold=True
                att=0
            
            action = self.listen(session, hold=hold)
            
            # Check for exit commands immediately
            if "die" in action or "shut down" in action:
                self.voicebox.say("Stora, out!")
                break
            
            worked, data = self.respond(user_text=action, session=session)
            if not worked:
                print(f"DATA WAS NONE: \n\t\u2022 {data}")
                hold = False
                att += 1
                continue
            
            history.append(data)
            
            hold = True
            att = 0
            
        return history
        
    def respond(self,

                user_text:str,
                session:Session)->tuple[bool, str]:
        
        if not user_text or not self.store:
            return False, ""
  
        action = self.agent_runner.listen_to_user(user_text)
        if not action:
            self.is_talking = True
            self.voicebox.say(f"Sorry, I don't know what '{user_text}' implies. I can do reviews, hourly checks, check for ended shifts, just give me the word!")
            self.is_talking = False
            return False, ""
        
        data, mes = self.agent_runner.run_action(
            session=session,
            action=action, 
            workers=WorkerServices()
            .get_workers_working(session,store=self.store))
        
        if not data:
            return False, mes
        
        speech_response = data.get('content')
        if speech_response:
            self.is_talking = True
            self.voicebox.say(speech_response)
            self.is_talking = False
        
        return True, data
    
    def listen(self, session: Session, hold:bool=True):

        if hold:
            self.ears.wait_for_wake_word()

            self.voicebox.say(random.choice(['yes?', 
                                        "i'm all ears", 
                                        'listening', 
                                        'yours truly', 
                                        "Yes human",
                                        "what is it now"]))
        att = 0
        while True:
            if att >= 3:
                return ""
            
            action = self.ears.sr_listen()
            if not action:
                self.voicebox.say(random.choice([
                    "I didn't quite catch that, can you please repeat", 
                    "My apologies, I didnt catch that", 
                    "please repeat that",
                    "huh?"]))
                att += 1
                continue
            return action
        
    def greet(self):
        try:
            self.is_talking = True
            self.voicebox.say(f"Hey, I am Stora. Your most helpful manager for {self.store.name}. I am delighted to work with all the great humans!")
            self.is_talking = False
            return True
        except Exception as ex:
            print(f"ERROR DURING GREET: \n\t\u2022 {ex}")
            return False
        
    def review(self, session:Session)->tuple[ErrorOccuredBool,dict]:
        self.is_busy = True
        workers = WorkerServices().get_workers_working(session, store=self.store)
        info = self.agent_runner.review(workers)
        if info['error'].strip() != "":
            return True, info
        self.is_busy = False
        return False, info
    
    def obtain_ended_shift(self, session:Session)->tuple[ErrorOccuredBool, dict]:
        data = self.timemanager.check(session=session)
        if data['error'].strip() != "":
            return True, data
        return False, data
    
    def _setup_and_edit_timemanager(self, store):
        return timemanager.TimeManager(store=store)
