from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_config import app, get_session
from sqlmodel import Session
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from agents.timemanager import TimeManager

time_manager = TimeManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background task when the server starts
    loop_task = asyncio.create_task(time_manager.hourly_check_loop())
    yield
    # Clean up when the server stops
    loop_task.cancel()

@app.get("/workers/shift-over")
def fetch_ended_shift(session: Session = Depends(get_session)):
    