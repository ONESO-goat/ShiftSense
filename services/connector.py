from sqlmodel import Session
import random
from models import Store, StoreStora
from agents import shiftmanager, timemanager  # Your existing logic class
from typing import TYPE_CHECKING
from worker_services import WorkerServices
if TYPE_CHECKING:
    from voicebox import listen, speak
    
class Connector:

    def respond(self,
                store:Store,
                user_text:str,
                session:Session,
                voicebox:"speak.Voice"):
        if not user_text or not store:
            return ""
        the_timemanager = self._setup_and_edit_timemanager(store)
        agent_runner = shiftmanager.Stora(store=store, timemanager=the_timemanager)
        action = agent_runner.listen_to_user(user_text)
        if not action:
            return f"Sorry, I don't know what '{action}' is. I can do reviews, hourly checks, check for ended shifts, just give me the word!"
        
        data = agent_runner.run_action(session=session,action=action, workers=WorkerServices().get_workers_working(session,store=store))
        if not data:
            return ""
        
        speech_response = data['content']
        voicebox.say(speech_response)
        return data
    
    def listen(self, 
               session: Session, 
                store:"Store",
                ears:"listen.Ears", 
                voicebox:"speak.Voice",
                user_message: str):

        while True:
            if ears.wait_for_wake_word():
                break
        att = 0
        voicebox.say(random.choice(['yes?', 
                                    "i'm all ears", 
                                    'listening', 
                                    'yours truly', 
                                    "Yes human",
                                    "what is it now"]))
        while True:
            if att >= 3:
                return ""
            
            action = ears.sr_listen()
            if not action:
                voicebox.say(random.choice(["I didn't quite catch that, can you please repeat", 
                                            "My apologies, I didnt catch that", 
                                            "please repeat that",
                                            "huh?"]))
                att += 1
                continue
            return action

    def _setup_and_edit_timemanager(self, store):
        return timemanager.TimeManager(store=store)
