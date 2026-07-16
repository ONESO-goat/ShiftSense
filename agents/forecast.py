from datetime import datetime
from helpers.config import Config

class Weather:
    NONE = ""
    SUNNY = "sunny"
    WINDY = "windy"
    CLOUDY = "cloudy"
    STORM = {
        "THUNDER", "HAIL", "SAND"
    }
    RAIN = {
        "HARSH", "MILD", "LOW"
    }
    SNOW = {
        "HARSH", "MILD", "LOW"
    }
    
class Forecast:
    def __init__(self, 
                 current_day:int|None=None):
        
        self.current_day = current_day if current_day is not None else datetime.now().date().day
        
        self.local_events = []
        
        self.weather: str = Weather.NONE

        self.holiday:str|None = None
        
    def get_local_events(self):
        # TODO: API KEY to get local events and its importance
        ...
        
    def get_weather(self):
        # TODO: API KEY to get local weather
        ...
        
    def get_holidays(self):
        # TODO: API KEY maybe for a calender to obtain holiday logic
        ...
    
    def update_date(self):
        self.current_day = datetime.now().date().day