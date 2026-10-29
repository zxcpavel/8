from contextlib import asynccontextmanager
from fastapi import FastAPI

from . import routers
from .database import engine
from .errors import register_handlers
from .models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="College API — вариант 4 (Стипендия)",
    description="Практическая работа №8. Общее ядро: студенты, группы, предметы, преподаватели. "
                "Вариант 4: стипендии, GET /api/scholarships/high, правило повышенной стипендии.",
    version="1.0.0",
    lifespan=lifespan,
)
register_handlers(app)

for r in (routers.groups, routers.teachers, routers.subjects, routers.students, routers.scholarships):
    app.include_router(r)
