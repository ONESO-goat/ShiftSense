from pydantic import BaseModel, Field
from enum import Enum
   
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
    ENG = "engineering"
    CASHIER = "cashier"
    CARTS = "cart push"
    MANAGER = "manager"
    ASSI_MANAGER = "assistant manager"
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
    schedule_list:list = Field(examples=[{
        "monday": {
            "shift_start": 8,
            "shift_end": 16,
            "is_off": False,
            "reason": ""
        },
        "tuesday": {
            "shift_start": 8,
            "shift_end": 16,
            "is_off": False,
            "reason": ""
        },
        "wednesday": {
            "shift_start": None,
            "shift_end": None,
            "is_off": True,
            "reason": "medical"
        },
    }]
                               )
class WorkerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50, examples=["Alice Smith"])
    department: DepartmentEnum = Field(default=DepartmentEnum.OPS)
    pay: int = Field(ge=0, description="Hourly rate or salary, must be positive", examples=[25])

class WorkerSchedule(BaseModel):
    """Groups the entire week into a single validated container."""
    worker_id: int
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
    pay: int
    schedule: WorkerSchedule  # Fully parsed structured dictionary

    class Config:
        # Crucial for SQLModel compatibility: allows Pydantic to read raw database objects
        from_attributes = True 