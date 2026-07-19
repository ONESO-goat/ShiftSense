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
    
    def get_store(self, session: Session, id:int|None=None, name:str="", city:str="", address:str="",zip:int=0):
        if not id and not name:
            raise ValueError("ID or worker name is required")
        
        if id:
            return session.get(Store, id)
        
        if not name or not address or not zip:
            raise ValueError("Store name, address, and zip are required for non-id search")
        
        kwargs = {
            "name": name,
            "city": city,
            "address": address,
            "zip": zip
        }
        conditions = [
            getattr(Store, key) == value
            for key, value in kwargs.items()
            if value is not None
        ]
        statement = select(Store).where(*conditions)
        
        return session.exec(statement).first()
    
    def store_exist(self, session:Session, name:str, zip:int, address:str)->bool:
        return self.get_store(session=session, name=name, zip=zip, address=address) is not None
    
    def create_store(self, 
                     session:Session, 
                     name:str, 
                     store_email:str, 
                     address:str, 
                     city:str, 
                     zip:int,
                     password:str)->dict[str, Any]:
        
        try:
            if self.store_exist(session=session, name=name, zip=zip, address=address):
                return {
                "created": False,
                "store":None,
                "errors": "This store already has a webpage, if you forgot id or password; click 'forgot id or password'"
            }
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
    
    def validate_login(self, session:Session, store_id, password):
        store = self.get_store(session=session, id=store_id)
        
        if not store or not verify_password(password, store.password):
            return None, f'username or password are invalid'
        return store, "welcome back!"
        
        
    def change_password(self, session:Session, new_password:str, store)->tuple[Store|None, str]:
        if not store:
            return None, "Store is required"
        
        valid, mes = validate_password(new_password)
        if not valid:
            return None, mes
        
        hashed_password = hash_password(password=new_password)
        store.password = hashed_password
        
        session.commit()

        return store, "Password successfully changed"