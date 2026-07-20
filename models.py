
import random
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from sqlmodel import Column, SQLModel, Field, JSON, Session, Relationship
from fastapi_config import get_session


# ================== ENUM OR HELPER =================

class SessionNotFoundError(Exception):
    pass


  
# =================== SQL MODELS ===================       
def create_id()->int:
    
    # session:Session = next(get_session())
    # if not session:
    #     raise SessionNotFoundError("The session wasn't found")
    return random.randint(1000000000, 9999999999)

    # while True:
    #     new_id = random.randint(1000000000, 9999999999)
    #     if not session.get(Worker, new_id):
    #         return new_id
        
class Store(SQLModel, table=True):
    id: str = Field(default=create_id(), primary_key=True)
    password:str
    name: str
    email:str
    address: str
    city: str
    zip: int
    
    workers: List['Worker'] = Relationship(back_populates="works_for")
    log: Optional['HistoryLog'] = Relationship(back_populates="store")
    
    schedule: dict[str, tuple[int,int]|None] = Field(default_factory=dict, sa_column=Column(JSON))

class Worker(SQLModel, table=True):
    id: str = Field(default=create_id(), primary_key=True)
    name: str
    department: str
    pay: float
    
    store_id: Optional[str] = Field(default=None, foreign_key="store.id")
    works_for: Optional["Store"] = Relationship(back_populates="workers")
    
    schedule: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    
class HistoryLog(SQLModel, table=True):
    id: str = Field(default=create_id(), primary_key=True)
    
    store_id: Optional[str] = Field(default=None, foreign_key="store.id")
    store: Optional['Store'] = Relationship(back_populates="log")
    
    log: list[Dict[str, Any]] = Field(default_factory=list, sa_type=JSON)
    

# class StoreStora(SQLModel, table=True):
#     id: str = Field(default=create_id, primary_key=True)
    
#     agent_settings: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
#     store_id: Optional[str] = Field(default=None, foreign_key="store.id")
#     store: Optional[Store] = Relationship(back_populates="agent")



    
# ==================================================

