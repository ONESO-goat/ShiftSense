from models import Store
from schemas import WorkerSchedule, DaySchedule
from sqlmodel import Session, select
from datetime import datetime
from .helpers import hash_password, verify_password, generate_secure_password, validate_password
from pydantic import ValidationError
from typing import Any




class StoreService:
    def __init__(self)->None:
        pass
    
    def get_all_stores(self, session: Session):
        statement = select(Store)
        return session.exec(statement).all()
    
    def get_store(self, session: Session, id:int|None=None, name:str="", address:str="",zip:int=0):
        if not id and not name:
            raise ValueError("ID or worker name is required")
        
        if id:
            return session.get(Store, id)
        
        if not name or not address or not zip:
            raise ValueError("Store name, address, and zip are required for non-id search")
        
        
        statement = select(Store).where(Store.name == name, 
                                        Store.address == address,
                                        Store.zip == zip)
        
        return session.exec(statement).first()
    
    def create_store(self, 
                     session:Session, 
                     name:str, 
                     store_email:str, 
                     address:str, 
                     city:str, 
                     zip:int,
                     password:str)->dict[str, Any]:
        
        try:
            validate_password(password=password)
            hashed_password = hash_password(password=password)
            store = Store(name=name, 
                          address=address,
                          email=store_email,
                          city=city, 
                          zip=zip,
                          password=hashed_password)
            
            session.add(store)
            session.commit()
            session.refresh(store)
            return {
                "created": True,
                "store":store,
                "errors": ""
            }
        except Exception as ex:
            session.rollback()
            print(f"Error during store creation process: \n\t\u2022 {ex}")
            return {
                "created": False,
                "store":None,
                "errors": f"Error during store creation process: \n\t\u2022 {ex}"
            }
    
    def update_password(self, session:Session, store_id):
        store = self.get_store(session=session, id=store_id)
        if not store:
            return None
        