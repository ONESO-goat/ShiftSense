from faster_whisper import WhisperModel
import random
import speech_recognition as sr
from typing import TYPE_CHECKING

    

class Ears:
    def __init__(self, use_whisper:bool=False):
        self.wav_file_path = "voicebox/audio/user_audio.wav"
        self.whisper_model = None
        if use_whisper:
            self.whisper_model = WhisperModel(self.wav_file_path)

        self.recognizer = sr.Recognizer()
        assert self.recognizer is not None, "Reconizer wasn't configured"
    
    def wait_for_wake_word(self, wake_word: str = "stora") -> bool:
        """
        Loops indefinitely, listening for a short snippet of audio.
        Returns True when the wake word is detected, returns 'random' for the mimic to say something random
        """
        print(f"Passive listening... Say '{wake_word}' to activate.")
        try:
            with sr.Microphone() as source:      
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                while True:
                
                        try:

                            audio_stream = self.recognizer.listen(source, timeout=None, phrase_time_limit=3)
                            text_result = self.recognizer.recognize_google(audio_stream).lower()

                            if wake_word in text_result:
                                print(f"Wake word '{wake_word}' detected!")
                                return True
                        
                        except sr.WaitTimeoutError:
                            continue
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as e:
                            print(f"API service error in passive loop: {e}")
                            continue
                        
                        except Exception as ex:
                            print(f"Possible error?: \n\t\u2022 {ex}")
                            continue
                        
        except KeyboardInterrupt:
            print("Passive listening interrupted by user.")
            raise

    def sr_listen(self, silence_timeout: float = 1.6, dynamic_energy: bool = False):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please stay quiet.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)

            self.recognizer.pause_threshold = silence_timeout
            self.recognizer.non_speaking_duration = 0.8  # closer to pause_threshold = more tolerant of trailing words

            if dynamic_energy:
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.dynamic_energy_ratio = 1.2  # less aggressive than 1.5 if you do use it
            else:
                self.recognizer.dynamic_energy_threshold = False
                # bump the static threshold above ambient adjust result with a floor,
                # since a too-low static threshold picks up noise as speech
                self.recognizer.energy_threshold = max(self.recognizer.energy_threshold, 300)

            print("Listening... Speak now.")

            try:
                audio_stream = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("Transcribing your audio...")
                text_result = self.recognizer.recognize_google(audio_stream)
                print(f"Heard: {text_result}")
                return text_result

            except sr.WaitTimeoutError:
                print("Error: You didn't start speaking within 10 seconds.")
                return ""
            except sr.UnknownValueError:
                print("Could not understand the audio (or you just cleared your throat/coughed).")
                return ""
            except sr.RequestError as e:
                print(f"API service error: {e}")
                return ""
            except KeyboardInterrupt:
                exit()
            except RuntimeError:
                print("Process stood stale and we are now breaking away")
                return ""
            
    def wav_breakdown(self, path="audio/audio.wav"):
        try:
            segments, info = self.whisper_model.transcribe(path)

            text = " ".join([s.text for s in segments]).strip()
            
            return text

        except Exception as e:
            print("Whisper error:", e)
            return ""
        
        
    