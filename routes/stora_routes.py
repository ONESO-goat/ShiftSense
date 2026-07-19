from services.store_services import StoreService
from services.connector import Connector
from fastapi_config import get_session, app
from fastapi import Depends, HTTPException
from sqlmodel import Session
from schemas import StoreCreate

# Stora is spelt correctly, that is the name of the agent: "Stora"

store_service = StoreService()

@app.post("/stora/run/{store_id}")
def fetch_interface_loop(store_id, session:Session=Depends(get_session)):
    store = store_service.get_store(session,id=store_id)
    if not 
    link = Connector()
@app.post("/stora/review")
def fetch_store_review(session:Session=Depends(get_session)):
    review = store_service
    
@app.get("/stora/{store_id}")
def fetch_store(store_id,session:Session=Depends(get_session)):
    store = store_service.get_store(session=session, id=store_id)
    if not store:
        raise HTTPException(status_code=403, detail=f"Store was not found with this id '{store_id}'")
    return store


@app.post("/stora/listen")
def fetch_stora_listening(session:Session = Depends(get_session)):
    """Stora listens for commands to run"""
    pass