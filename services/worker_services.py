from models import Worker, Store
from schemas import WorkerSchedule, DaySchedule
from sqlmodel import Session, select
from datetime import datetime
from pydantic import ValidationError


class WorkerServices:
    
    def get_all_workers(self, session: Session, store:'Store|None'=None):
        
        if store is not None:
            if not session.get(Store, store.id):
                raise ValueError("Store doesnt exist while getting all workers from there")
            statement = select(Worker).where(Worker.store_id==store.id)
            
        else:
            statement = select(Worker)
            
        return session.exec(statement).all()
    
    def get_worker(self, session: Session, id:int|None=None, name:str=""):
        if not id and not name:
            raise ValueError("ID or worker name is required")
        
        if id:
            return session.get(Worker, id)
        
        statement = select(Worker).where(Worker.name == name)
        return session.exec(statement).first()
    
    def assign_schedule(self, session: Session, payload: WorkerSchedule) -> Worker | None:
      
        worker = session.get(Worker, payload.worker_id)
        if not worker:
            return None  
            
        
        schedule_data = payload.model_dump(exclude={"worker_id"})
        
        worker.schedule = schedule_data
        
        self.save_and_commit_data(session=session, object=worker)
        return worker


    def create_worker(self, 
                      session: Session, 
                      name:str, 
                      department:str, 
                      pay:int,
                      schedule:WorkerSchedule|None=None):
        
        name_taken = self.get_worker(session=session, name=name)
        if name_taken is not None:
            print(f"The name '{name}' is already inside the known database. Adding it with numbering")
            name = f'{name} (2)'
            
        worker = Worker(
            name=name,
            department=department,
            pay=pay,
            schedule={}
        )
        self.save_and_commit_data(session=session, object=worker)
        return worker
    
    def remove_worker(self, session:Session, worker_id:int)->tuple[int, dict[str,str]]:

        if not worker_id:
            return 400, {"error": "Worker id was not included"}

        worker = self.get_worker(session=session, id=worker_id)
        if not worker:
    
            return 404,  {"error": f"Worker '{worker_id}' was not found"}
        
        session.delete(worker)
        return 200, {"message": f"Worker '{worker_id}' was successfully removed"}
    
    def _validate_schedule_structure(self, info: dict) -> DaySchedule | None:
        try:

            return DaySchedule(**info)
        except ValidationError as ex:

            print(f"Day structure is not valid: {ex}")
            return None
    
    def get_workers_working(self, session:Session, store)->list['Worker']:
        workers = self.get_all_workers(session=session,store=store) 
        
        weekday = datetime.now().strftime("%A").lower()
        
        return [
            worker for worker 
            in workers 
            if worker.schedule.get(weekday, "")
            .get("is_off", "") 
            is False
                  ]
    
        
    def build_schedule(self, schedule:dict|WorkerSchedule)->WorkerSchedule|None:
        
        try:
            # if len(schedule.keys()) != 7:
            #     print(f"Weekday length isnt valid: {len(schedule)} days recored instead of 7")
            #     return None
            
            # validated_days = {}
            
            # for day_name, info in schedule.items():
            #     validated_day = self._validate_schedule_structure(info)
            #     if validated_day is None:
            #         print(f"Validation failed on day: {day_name}")
            #         return None
                
            #     validated_days[day_name] = validated_days
                
            return WorkerSchedule(**schedule)
        
        except ValidationError as ex:
            print(f"Schedule validation failed: {ex}")
            return None   
        
    def save_and_commit_data(self, session: Session, object):
        
        session.add(object)
        session.commit()    # Saves it permanently
        session.refresh(object) 
    
    
        

