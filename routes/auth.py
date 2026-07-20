# auth.py


from services.store_services import StoreService
from fastapi_config import get_session, app
from fastapi import Depends, HTTPException
from sqlmodel import Session
from schemas import StoreLogin, StoreCreate, StoreInfo

store_service = StoreService()

@app.post("/stora/make")
def fetch_build_store(data:StoreCreate,session:Session=Depends(get_session)):
    info = store_service.create_store(session=session, **data.model_dump())
    if not info['created']:
        raise HTTPException(status_code=500, detail=info['errors'])
    return info['store']

@app.post("/stora/login")
def fetch_store_login(data:StoreLogin,session:Session=Depends(get_session)):
    store, mes = store_service.validate_login(
        session=session,
        store_id=data.id, 
        password=data.password)
    if not store:
        raise HTTPException(status_code=400, detail=mes)
    
    return store


@app.post("/stora/get/data")
def fetch_store_data(data:StoreInfo,session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=None, **data.model_dump())
    if not store:
        raise HTTPException(status_code=400, detail="This store doesn't exist, please double check info")
    
    return store.id

@app.get("/stora/forgot/id")
def fetch_store_id(email:str,session:Session=Depends(get_session)):
    store = store_service.get_store_by_email(session=session, email=email)
    if not store:
        raise HTTPException(status_code=400, detail=f"No store found with the email '{email}', please double check info")
    
    return store.id

@app.get("/stora/forgot/password/{store_id}")
def fetch_store_password_change(new_password:str, store_id:int, session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=store_id)
    if not store:
        raise HTTPException(status_code=400, detail="This store doesn't exist, please double check info")
    
    store, mes = store_service.change_password(session=session,store=store, new_password=new_password)
    if not store:
        raise HTTPException(status_code=400, detail=mes)
    
    return store.id