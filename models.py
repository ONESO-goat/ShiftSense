
import random
from typing import Dict, Any
from sqlmodel import Column, SQLModel, Field, JSON

# ================== ENUM OR HELPER =================

def create_id(self)->int:
        while True:
            new_id = random.randint(10000000, 90000000)
            if new_id in self.worker_database:
                continue
            
            return new_id
  
# =================== SQL MODELS ===================       

class Worker(SQLModel, table=True):
    id: str = Field(default=create_id, primary_key=True)
    name: str
    department: str
    pay: int
    
    schedule: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
# ==================================================

