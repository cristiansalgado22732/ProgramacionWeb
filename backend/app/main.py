import time
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from .routers import auth, tickets, users

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import Base, SessionLocal, engine
from .models import Role, User
from .security import hash_password


def init_db():
    for _ in range(10):  # la BD puede tardar unos segundos en aceptar conexiones
        try:
            Base.metadata.create_all(engine)
            break
        except OperationalError:
            time.sleep(2)
    else:
        raise RuntimeError("No se pudo conectar a la base de datos")

    with SessionLocal() as db:
        email = settings.admin_email.lower()
        if not db.scalar(select(User).where(User.email == email)):
            db.add(
                User(
                    name="Admin",
                    email=email,
                    password_hash=hash_password(settings.admin_password),
                    role=Role.admin,
                )
            )
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # se ejecuta una vez, al arrancar
    yield      # aquí la API atiende peticiones


app = FastAPI(title="HelpDesk API", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}

"""
@app.get("/api/hello/{name}")
def hello(name: str):
    return {"message": f"Hola, {name}"}
"""

api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(tickets.router)
api.include_router(users.router)
app.include_router(api)