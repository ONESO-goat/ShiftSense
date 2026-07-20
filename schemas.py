from pydantic import BaseModel, Field
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Store
   
class AbsenceReason(str, Enum):
    NONE = ""
    BREAK = "break"
    MEDICAL = "medical"
    ACCIDENT = "accident"
    EXCUSED = "excused"

class CloseReason(str, Enum):
    NONE = ""
    BREAK = "break"
    EMERGENCY = "emergency"
    WEATHER = "weather"
    EVENT = "event"
    

class DepartmentEnum(str, Enum):
    HR = "human resources"
    CS = "customer survice"
    ENG = "engineering"
    CASHIER = "cashier"
    CARTS = "carts"
    MANAGER = "manager"
    ASSISTANT_MANAGER = "assistant manager"
    OPS = "operations"
    SALES = "sales"
    
class DaySchedule(BaseModel):
    """Defines exactly what a single day's schedule looks like."""
    # 0 - 24 hour clock
    shift_start: int|None = Field(ge=0, le=24, description="Hour must be between 0 and 24")
    shift_end: int|None = Field(ge=0, le=24, description="Hour must be between 0 and 24")
    is_off: bool = False
    reason: AbsenceReason = Field(default=AbsenceReason.NONE)

class StoreDays(BaseModel):
    """Defines exactly what a single day's schedule looks like."""
    # 0 - 24 hour clock
    is_24_7: bool = False
    opened: int|None = Field(ge=0, le=24, description="Hour must be between 0 and 24")
    closed: int|None = Field(ge=0, le=24, description="Hour must be between 0 and 24")
    is_off: bool = False
    reason: CloseReason = Field(default=CloseReason.NONE)

    



# CLIENT INPUTS

class ScheduleCreate(BaseModel):
    schedule_list:list = Field(examples=[
        {
    "monday": {
        "shift_start": 8,
        "shift_end": 17,
        "is_off": False,
        "reason": ""
    },
    
    "tuesday": {
        "shift_start": 8,
        "shift_end": 17,
        "is_off": False,
        "reason": ""
    },
    "wednsday": {
        "shift_start": 8,
        "shift_end": 17,
        "is_off": False,
        "reason": ""
    },
    "thursday": {
        "shift_start": 8,
        "shift_end": 17,
        'is_off': False,
        "reason": ""
    },
    "friday": {
        "shift_start": 8,
        "shift_end": 17,
        "is_off": False,
        "reason": ""
    },
    "saturday": {
        "shift_start": 0,
        "shift_end": 0,
        "is_off": True,
        "reason": "break"
    },
    "sunday": {
        "shift_start": 0,
        "shift_end": 0,
        "is_off": True,
        "reason": "break"
    }
    }])
    
    
class WorkerUpdate(BaseModel):
    name: str | None = None
    department: DepartmentEnum | None = None
    pay: float | None = None
    
class WorkerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50, examples=["Alice Smith"])
    department: DepartmentEnum = Field(default=DepartmentEnum.CASHIER)
    pay: float = Field(ge=0, description="Hourly rate or salary, must be positive", examples=[25])
    
class StoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, examples=["Market Basket"])
    city: str = Field(min_length=1, max_length=50, examples=["boston"])
    email: str = Field(examples=["marketbasket66666@gmail.com"])
    address: str = Field(examples=["700 boston rd"])
    zip: int = Field( description="The zip of the location", examples=[66666])
    password:str =  Field(min_length=10, max_length=250, examples=["MyGoodPassword123"])

class StoreInfo(BaseModel):
    name: str = Field(min_length=1, max_length=50, examples=["Market Basket"])
    city: str = Field(min_length=1, max_length=50, examples=["boston"])
    email: str = Field(examples=["marketbasket66666@gmail.com"])
    address: str = Field(examples=["700 boston rd"])
    zip: int = Field( description="The zip of the location", examples=[66666])

class StoreLogin(BaseModel):
    id: int =  Field(examples=[1000000000])
    password: str =  Field(min_length=10, max_length=250, examples=["MyGoodPassword123"])

class WorkerSchedule(BaseModel):
    """Groups the entire week into a single validated container."""
    monday: DaySchedule
    tuesday: DaySchedule
    wednesday: DaySchedule
    thursday: DaySchedule
    friday: DaySchedule
    saturday: DaySchedule
    sunday: DaySchedule
    
class StoreSchedule(BaseModel):
    """Groups the entire week into a single validated container."""
    store_id: int
    monday: DaySchedule
    tuesday: DaySchedule
    wednesday: DaySchedule
    thursday: DaySchedule
    friday: DaySchedule
    saturday: DaySchedule
    sunday: DaySchedule
    
# API RESPONSE

class WorkerResponse(BaseModel):
    id: int  # Converted from the database auto-increment ID
    name: str
    department: DepartmentEnum
    pay: float
  
    schedule: WorkerSchedule  # Fully parsed structured dictionary

    class Config:
        # Crucial for SQLModel compatibility: allows Pydantic to read raw database objects
        from_attributes = True 