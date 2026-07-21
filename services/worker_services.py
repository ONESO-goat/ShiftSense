from models import Worker, Store
from schemas import WorkerSchedule, DaySchedule
from sqlmodel import Session, select, func
from datetime import datetime
from pydantic import ValidationError
import traceback


class WorkerServices:
    
    def get_all_workers(self, session: Session, store:'Store|int|None'=None):
        
        if store is not None:
            if isinstance(store, int):
                store = session.get(Store, store)
            if not store:
                return None
            statement = select(Worker).where(Worker.store_id==store.id)
            
        else:
            statement = select(Worker)
            
        return session.exec(statement).all()
    
    def get_worker(self, session: Session, store:Store|int|None=None, id:int|None=None, name:str=""):
        if isinstance(store, int):
            store = session.get(Store, store) 
            
        if not id and not name:
            raise ValueError("ID or worker name is required")
        
        
        if id:
            return session.get(Worker, id)
        
        if store is None:
            raise ValueError("Store is required")
        
        statement = select(Worker).where(Worker.name == name, Worker.store_id == store.id)
        return session.exec(statement).first()
    
    def get_workers_by_name(self, session: Session, store:Store|int|None=None, name:str=""):
        if isinstance(store, int):
            store = session.get(Store, store) 

        
        if not name or store is None:
            raise ValueError("Store and name are required")
        
        name = name.lower().strip()
        
        statement = select(Worker).where(
    func.lower(func.trim(Worker.name)) == name.lower().strip(),
    Worker.store_id == store.id
)
        return session.exec(statement).all()
        
    def assign_schedule(self, session: Session, worker_id:int, payload: WorkerSchedule) -> Worker | None:

        worker = self.get_worker(session=session, id=worker_id)
        if not worker:
            raise ValueError(f"Worker with id {worker_id} doesn't exist")
        
        sch = {}
        for day, info in payload.model_dump().items():
            try:
                sch[day] = self._validate_schedule_structure(info)
            except ValidationError as ex:
                raise ValidationError(f"'{day}' faced an error: {ex}")
            
        sch = self.build_schedule(sch)
        if not sch:
            raise ValidationError("Schedule doesnt follow the correct json structure")
        
        worker.schedule = sch.model_dump()
        
        
        session.commit()
        
        return worker


    def create_worker(self, 
                      session: Session, 
                      store_id:int,
                      name:str, 
                      department:str, 
                      pay:int|float,
                      schedule:WorkerSchedule|None=None):
        try:
            store = session.get(Store, store_id)
            if not store:
                return None
            
            name_taken = self.get_workers_by_name(session=session, name=name, store=store)
            num = 1
            if name_taken:
                print(f"The name '{name}' is already inside the known database for this store. Adding it with numbering")
                num = len(name_taken) + 1
                
            worker = Worker(
                name=name,
                department=department,
                pay=pay,
                same_name_id=num,
                works_for=store,
                schedule={}
            )
            session.add(worker)
            session.commit()
            return worker
        except Exception as ex:
            session.rollback()
            print(f"Error during work creation process: {ex}")
            return None
    
    def remove_worker(self, session:Session, worker_id:int, store_id:int|None=None)->tuple[int, dict[str,str]]:

        if not worker_id:
            return 400, {"error": "Worker id and Store id are required"}

        worker = self.get_worker(session=session, id=worker_id, store=None)
        if not worker:
    
            return 404,  {"error": f"Worker '{worker_id}' was not found"}
        
        session.delete(worker)
        session.commit()
        return 200, {"message": f"Worker '{worker_id}' was successfully removed"}
    
    def _validate_schedule_structure(self, info: dict) -> DaySchedule | None:
        try:

            return DaySchedule(**info)
        except ValidationError as ex:

            print(f"Day structure is not valid: {ex}")
            return None
    
    def get_workers_working(self, session:Session, store)->list['Worker']:
        try:
            workers = self.get_all_workers(session=session,store=store) 
            
            weekday = datetime.now().strftime("%A").lower()
            
            return [
                worker for worker 
                in workers 
                if worker.schedule.get(weekday, "")
                and 
                worker.schedule.get(weekday, "").get("is_off", "") 
                is False
                    ]
        except Exception as ex:
            print(f"ERROR DURING GETTING WORKERS WORKING: {ex}")
            print(traceback.print_exc())
            return []
    
        
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
    
    
        

