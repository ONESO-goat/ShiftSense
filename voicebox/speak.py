import pyttsx3
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Store
class Voice:
    def __init__(self, language:str="english", perferred_tts:str="piper") -> None:
        # We build pytts3 either way for a backup
        
        if not perferred_tts or perferred_tts.lower().strip() not in ['piper', 'edge', 'pyttsx', 'pyttsx3']:
            raise ValueError(f"'{perferred_tts}' is not a valid tts")
        if perferred_tts == 'pyttsx3': perferred_tts = "pyttsx"

        self.perferred_tts = perferred_tts.lower().strip()
        self.engine = pyttsx3.init()
        
        self.rate = self.engine.getProperty('rate') 
        
        self.volume = self.engine.getProperty("volume")
        
        
        self.languages = self.engine.getProperty('voices') 
        
        if any(x is None for x in [self.rate, self.volume, self.languages]):
            raise ValueError(f"""A text to speech config recieved None: 
                             \nVolume exist: {self.volume is not None}
                             \nVoices exist: {self.languages is not None}
                             \nRate exist: {self.rate is not None}
                             """)
            
        
        self.engine.setProperty('volume', 0.7)
        self.engine.setProperty('rate', 150)
        self.set_language(language=language)
        
        print("Voice configuration success ✅")
        
    def set_language(self, language: str):
        language = language.lower()

        for voice in self.languages:
            if language in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                return

        raise ValueError(f"No voice found for '{language}'") 
    
    def change_voice(self, gender_or_option:str):
        import random
        voices = {
            "male": 0,
            "female": 1,
            "random": random.randint(0, 1),
            "other": 1
        }
        gender_or_option = gender_or_option.lower().strip()
        if not gender_or_option or gender_or_option not in voices:
            raise ValueError(f"Parameter '{gender_or_option}' is invalid")
       
        if not self.languages:
            raise RuntimeError("No languages available.")
        
        self.engine.setProperty("voice", self.languages[voices[gender_or_option]].id)
        
    def change_rate(self, new_rate:int):
        if not 1 <= new_rate or new_rate <= 200:
            raise ValueError(f"{new_rate} is outside the valid range of 1-200")
        
        self.engine.setProperty("rate", new_rate)
        
    def change_volume(self, new_volume: int):
        if not 0 <= new_volume <= 10:
            raise ValueError("Volume must be between 0 and 10.")

        self.engine.setProperty("volume", new_volume / 10)
    
    def say(self, text:str, change_perferred_tts:str|None=None):
        if not text.strip():
            return
        text = text.lower().strip()
        #TODO: Helper to check if text is bad
        
        say_functions = {
            "edge": self._edge_tts_say,
            "pyttsx": self._pyttsx3_say,
            "piper": self._piper_say
        }
        if change_perferred_tts is not None and change_perferred_tts:
            self.perferred_tts = change_perferred_tts.lower().strip()
            
        say_functions[self.perferred_tts](text=text)

    def _edge_tts_say(self, text:str):
        import asyncio
        import edge_tts

        async def speak():
            communicate = edge_tts.Communicate(
                text,
                "en-US-AriaNeural"
            )
            await communicate.save("audio/edge.mp3")

        asyncio.run(speak())
        
    def _piper_say(self, text:str):
        piper_path = "voicebox/audio/piper.wav"
        subprocess.run(
            [
                "piper",
                "--model",
                "voicevox/audio/piper-voices/en_US-lessac-medium.onnx",
                "--config",
                "voicevox/audio/piper-voices/en_US-lessac-medium.onnx.json",
                "--output_file",
                piper_path,
            ],
            input=text,
            text=True,
            check=True,
        )
        self._aplay_file(piper_path)
        
    def _pyttsx3_say(self, text:str):
        
        if not text.strip():
            return
        
        self.engine.say(text)
        self.engine.runAndWait()
        
    def get_available_languages(self):
        for i, voice in enumerate(self.engine.getProperty("voices")):
            print(f"Index: {i}")
            print(f"Name: {voice.name}")
            print(f"ID: {voice.id}")
            print(f"Languages: {getattr(voice, 'languages', None)}")
            print()
        
    def _aplay_file(self, file_path: str | Path):
        subprocess.run(
            ["aplay", str(file_path)],
            check=True
        )