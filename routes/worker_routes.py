# worker_service.py

from services.worker_services import WorkerServices
from fastapi_config import get_session, app
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from schemas import WorkerCreate, WorkerResponse, WorkerSchedule, ScheduleCreate, WorkerUpdate

worker_service = WorkerServices()

@app.get("/workers", response_model=list[WorkerResponse])
def fetch_all_workers(session: Session = Depends(get_session)):
    return worker_service.get_all_workers(session)

@app.get("/workers/{worker_id}", response_model=list[WorkerResponse])
def fetch_worker(worker_id:int, session: Session = Depends(get_session)):
    worker = worker_service.get_worker(session=session, id=worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker {worker_id} does not exist")
    return worker

@app.post("/worker/add", response_model=WorkerResponse)
def fetch_add_worker(
    worker_data: WorkerCreate,               
    session: Session = Depends(get_session) 
):
    try:
      
        new_worker = worker_service.create_worker(
            session=session,
            name=worker_data.name,
            department=worker_data.department.value,
            pay=worker_data.pay
        )
        return {"message": "Worker added successfully", "worker": new_worker}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/worker/remove/{worker_id}")
def fetch_remove_worker(
    worker_id:int,
    session: Session = Depends(get_session)
):
    try:
        code, mess = worker_service.remove_worker(session=session, worker_id=worker_id)
        if code != 200:
            raise HTTPException(status_code=code, detail=mess)
        return {"message": mess}
    
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/worker/schedule/{worker_id}")
def fetch_fix_worker_schedule(
    worker_id:int, 
    schedule: WorkerSchedule,
    session:Session = Depends(get_session)
):
    """
    Logic: When the admin press 'save', everything gets saved
    """
    if not schedule or not worker_id:
        raise HTTPException(status_code=400, detail="Schedule or worker_id are required")

    if worker_id != schedule.worker_id:
        raise HTTPException(
                status_code=400, 
                detail="URL worker_id does not match the payload worker_id"
            )
            
    if not schedule.worker_id:
            schedule.worker_id = worker_id
            
    updated_worker = worker_service.assign_schedule(session, schedule)
    if not updated_worker:
        raise HTTPException(
                status_code=400, 
                detail=f"Worker with ID {worker_id} not found"
            )
            
    return {"message": "successfully updated user schedule"}

    
    
@app.patch("/worker/update/{worker_id}")
def fetch_update_worker_info(
    worker_id:int,
    worker_data: WorkerUpdate,
    session:Session = Depends(get_session)
):
    worker = worker_service.get_worker(session=session, id=worker_id)
    if not worker:
        raise HTTPException(status_code=400, detail=f"Worker {worker_id} does not exist")
    

    if worker_data.pay > 50:
        raise HTTPException(status_code=400, 
                            detail=f"Worker pays does not seem suitable, please double check 'pay' field")
    
    worker.name = worker_data.name
    worker.department = worker_data.department.value
    
    worker.pay = worker_data.pay
    session.commit()
    session.refresh(worker)
    return worker