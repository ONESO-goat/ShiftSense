# time_routes.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_config import app, get_session
from sqlmodel import Session
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from agents import timemanager, shiftmanager
from services.store_services import StoreService

store_service = StoreService()

@asynccontextmanager
async def lifespan(stora, session:Session=Depends(get_session)):
    # Start the background task when the server starts

    loop_task = asyncio.create_task(stora.time_manager.hourly_check_loop())
    yield
    # Clean up when the server stops
    loop_task.cancel()

@app.get("/workers/shift-over")
def fetch_ended_shift(session: Session = Depends(get_session)):
    return time_manager.get_ended_shift()

    