from datetime import datetime
from helpers.config import Config
import holidays
import requests
import serpapi


class Weather:
    NONE = ""
    SUNNY = "sunny"
    WINDY = "windy"
    CLOUDY = "cloudy"
    

    STORM = {"THUNDER", "HAIL", "SAND"}
    RAIN = {"HARSH", "MILD", "LOW"}
    SNOW = {"HARSH", "MILD", "LOW"}
    
class Forecast:
    def __init__(self, current_day: int | None = None):
        self.current_day = current_day if current_day is not None else datetime.now().date().day
        self.date = str(datetime.now().date())
        
        self.holidays = holidays.US()
        self.local_events = []
        
        self.weather: str = Weather.NONE
        self.temperature: int | None = None
        self.holiday: str | None = None
        
    def get_local_events(self):
        client = serpapi.Client(api_key=Config.serpapi_api_key)

        # Set up query parameters targeting specific locations
        results = client.search({
            "engine": "google_events",
            "q": f"Events in {Config.location}", 
            "hl": "en",
            "gl": "us"
        })

        events_list = results.get("events_results", [])
        formatted_events = []
        
        for idx, event in enumerate(events_list, 1):
            formatted_events.append({
                "id": idx,
                "title": event.get('title'),
                "start_time": event.get('date', {}).get("start_time"),
                "venue": event.get('venue', {}).get('name'),
                "location": event.get('venue', {}).get('address'),
                "thumbnail_url": event.get('thumbnail')
            })
            
        self.local_events = formatted_events
        return formatted_events

    def get_weather(self) -> dict | None:
        cfg = Config()
    
        query_params = {
            'q': cfg.location,
            'appid': cfg.weather_app_api,
            'units': 'metric' 
        }
        
        try:
            response = requests.get(cfg.weather_base_url, params=query_params)
            response.raise_for_status()
            
            weather_data = response.json()
            
            if "main" in weather_data and "temp" in weather_data["main"]:
                self.temperature = round(weather_data["main"]["temp"])
            
            # Map weather conditions using OpenWeatherMap condition codes
            if "weather" in weather_data and len(weather_data["weather"]) > 0:
                weather_id = weather_data["weather"][0]["id"]
                main_condition = weather_data["weather"][0]["main"].lower()
                
                # OpenWeatherMap ID mapping codes (2xx=Storm, 3xx/5xx=Rain, 6xx=Snow)
                if 200 <= weather_id < 300:
                    self.weather = "THUNDER"  # Belongs to Weather.STORM
                elif 300 <= weather_id < 600:
                    self.weather = "MILD" if weather_id in [300, 500, 501] else "HARSH" # Belongs to Weather.RAIN
                elif 600 <= weather_id < 700:
                    self.weather = "MILD" if weather_id == 600 else "HARSH" # Belongs to Weather.SNOW
                elif weather_id == 800:
                    self.weather = Weather.SUNNY
                elif 801 <= weather_id <= 804:
                    self.weather = Weather.CLOUDY
                else:
                    self.weather = Weather.NONE

            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
                    
    def get_holidays(self):
        return self.holidays
    
    def is_holiday(self) -> tuple[bool, str]:
        today = datetime.today().date()
        if today in self.holidays:
            self.holiday = self.holidays.get(today).lower() 
            if self.holiday:
                return True, self.holiday
        
        self.holiday = ''
        return False, ''
    
    @property
    def current_date(self):
        return datetime.now().date().isoformat()
    
    @property
    def current_weekday(self):
        return datetime.now().strftime("%A").lower()
    
    def update_date(self):
        self.current_day = datetime.now().date().day
        self.date = datetime.now().date().isoformat()
        
