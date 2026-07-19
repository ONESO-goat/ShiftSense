
import random
from typing import Dict, Any
from sqlmodel import Column, SQLModel, Field, JSON, Session
from fastapi_config import get_session

# ================== ENUM OR HELPER =================

class SessionNotFoundError(Exception):
    pass

def create_id()->int:
    
    session:Session = get_session()
    if not session:
        raise SessionNotFoundError("The session wasn't found")
    
    while True:
        new_id = random.randint(1000000000, 9999999999)
        if not session.get(Worker, new_id):
            return new_id
  
# =================== SQL MODELS ===================       

class Worker(SQLModel, table=True):
    id: str = Field(default=create_id, primary_key=True)
    name: str
    department: str
    pay: int
    
    schedule: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
class Store(SQLModel, table=True):
    id: str = Field(default=create_id, primary_key=True)
    
    name: str
    address: str
    city: str
    zip: int
    
    schedule: dict[str, tuple[int,int]|None] = Field(default_factory=dict, sa_column=Column(JSON))
    
# ==================================================

