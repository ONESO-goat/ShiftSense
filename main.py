# main.py
from fastapi_config import app, create_db_and_tables

import routes.auth
import routes.stora_routes
import routes.time_routes
import routes.worker_routes  

create_db_and_tables()

@app.get("/")
def read_root():
    return {"status": "Server is running!"}