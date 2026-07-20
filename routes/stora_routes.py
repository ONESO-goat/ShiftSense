# stora_routes.py


from services.store_services import StoreService
from services.connector import Connector
from fastapi_config import get_session, app
from voicebox import speak, listen
from fastapi import Depends, HTTPException
from sqlmodel import Session
from schemas import StoreCreate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Store
# Stora is spelt correctly, that is the name of the agent: "Stora"

store_service = StoreService()

ErrorString = str


def assign_link(store:'Store|int', session:Session)->tuple[bool,'ErrorString|Connector']:
    try:
    
        if isinstance(store, int):
            store = store_service.get_store(session=session,id=store)
            
        if not store:
            return False, "Store does not exist"
                
        link = Connector(store=store, ears=listen.Ears(), voicebox=speak.Voice())
        if not link:
            return False, "Error occured during linking process"
        
        return True, link
    
    except Exception as ex :
        print(f"Error occured during process: {ex}")
        return False, str(ex)
        
def speaking_to_agent_loop(store:'Store|int', session:Session)->tuple[bool,ErrorString|list[dict]]:
    try:
    
        if isinstance(store, int):
            store = store_service.get_store(session=session,id=store)
            
        if not store:
            return False, "Store does not exist"
                
        link = Connector(store=store, ears=listen.Ears(), voicebox=speak.Voice())
        if not link:
            return False, "Error occured during linking process"
        
        data = link.process(session=session)
        return True, data
    
    except Exception as ex:
        print(f"Error occured during process: {ex}")
        return False, str(ex)
    
    except KeyboardInterrupt:
        return True, "Broken"

@app.get("/workers/shift-over/{store_id}")
def fetch_ended_shift(store_id:int, session: Session = Depends(get_session)):
    success, link = assign_link(store_id, session=session)
    if not success or isinstance(link, ErrorString):
        raise HTTPException(status_code=400, detail=link)
    shifts = link.timemanager.check(session)
    return shifts

@app.post("/stora/talk/{store_id}")
def fetch_talk_to_agent(store_id:int, session=Depends(get_session)):
    success, link = assign_link(store=store_id, session=session)
    if not success or isinstance(link, ErrorString):
        raise HTTPException(status_code=400, detail=link)
    data = link.process(session=session)
    return data
    
    

        
@app.post("/stora/review/{store_id}")
def fetch_store_review(store_id:int, session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=store_id)
    if not store:
        raise HTTPException(status_code=400, detail=f"Store with the id {store_id} does not exist")
    worked, link = assign_link(store=store,session=session)
    if not worked or isinstance(link, ErrorString):
        raise HTTPException(status_code=400, detail=link)
    
    error_occured, data = link.review(session=session)
    if error_occured:
        raise HTTPException(status_code=400, detail=data['error'])
    return data


@app.post("/stora/ended-shift/{store_id}")
def fetch_store_ended_shift(store_id:int, session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=store_id)
    if not store:
        raise HTTPException(status_code=400, detail=f"Store with the id {store_id} does not exist")
    worked, link = assign_link(store=store,session=session)
    if not worked or isinstance(link, ErrorString):
        raise HTTPException(status_code=400, detail=link)
    
    error_occured, data = link.obtain_ended_shift(session=session)
    if error_occured:
        raise HTTPException(status_code=400, detail=data['error'])
    return data
    
    
@app.get("/stora/{store_id}")
def fetch_store(store_id:int,session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=store_id)
    if not store:
        raise HTTPException(status_code=403, detail=f"Store was not found with this id '{store_id}'")
    
    return store

