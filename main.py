# main.py
from fastapi_config import app

import routes.auth
import routes.stora_routes
import routes.time_routes
import routes.worker_routes  


@app.get("/")
def read_root():
    return {"status": "Server is running!"}