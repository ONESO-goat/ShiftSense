from services.store_services import StoreService
from fastapi_config import get_session, app
from fastapi import Depends, HTTPException
from sqlmodel import Session
from schemas import StoreLogin


@app.post("/stora/login")
def fetch_store_login(data:StoreLogin,session:Session=Depends(get_session)):
    

