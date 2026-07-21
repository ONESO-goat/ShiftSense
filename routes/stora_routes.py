# stora_routes.py


from services.store_services import StoreService
from services.connector import StoraSession
from services.connector_gemini import GeminiStoraSession
import asyncio
from fastapi_config import get_session, app
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from schemas import StoreCreate
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from models import Store
# Stora is spelt correctly, that is the name of the agent: "Stora"

store_service = StoreService()

ErrorString = str


def assign_link(store:'Store|int', session:Session, version:str="normal")->tuple[bool,'ErrorString|Any']:
    try:
    
        if isinstance(store, int):
            store = store_service.get_store(session=session,id=store)
            
        if not store:
            return False, "Store does not exist"
        if version == "gemini":
            link = GeminiStoraSession(store=store)
        else:
            link = StoraSession(store=store)
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
                
        link = StoraSession(store=store)
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
def old_fetch_talk_to_agent(store_id:int, session=Depends(get_session)):
    success, link = assign_link(store=store_id, session=session)
    if not success or isinstance(link, ErrorString):
        raise HTTPException(status_code=400, detail=link)
    
    link.greet()
    data = link.process(session=session)
    return data
    
@app.websocket("/stora/talk/ws/{store_id}")
async def websocket_talk_to_agent(websocket: WebSocket, store_id: int, session: Session = Depends(get_session)):
    await websocket.accept()
    
    success, link = assign_link(store=store_id, session=session, version="gemini")
    if not success or isinstance(link, ErrorString):
        await websocket.close(code=4000)
        return
        
    # 1. Immediately send the text greeting down the wire for the frontend to speak
    await websocket.send_json({"type": "speak", "text": link.greet_text()})
    
    att = 0
    try:
        while True:
            # 2. Wait for the frontend to stream a message/transcript over the network
            action = await websocket.receive_text()
            
            if "die" in action or "shut down" in action:
                await websocket.send_json({"type": "speak", "text": "Shutting down session."})
                await websocket.close()
                break
            
            # 3. Pass text to agent logic
            worked, response_data = await link.respond(user_text=action, session=session)
            
            if not worked:
                att += 1
                # If agent fails, provide a fallback message string
                error_msg = response_data if response_data else "I didn't quite catch that, can you repeat?"
                await websocket.send_json({"type": "speak", "text": error_msg})
                
                if att >= 3:
                    await websocket.send_json({"type": "speak", "text": "System resetting attempt counter."})
                    att = 0
                continue
            
            # 4. Stream successful analytical data and speech text back to client
            speech_response = response_data.get('content', '')
            await websocket.send_json({
                "type": "data",
                "speech_text": speech_response,
                "payload": response_data
            })
            att = 0

    except WebSocketDisconnect:
        print(f"Store {store_id} client disconnected normally from agent.")
    

        
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

