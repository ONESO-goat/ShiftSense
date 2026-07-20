# uvicorn main:app --reload
import fastapi
from sqlmodel import Session, create_engine

app = fastapi.FastAPI(title="Stora API")

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


