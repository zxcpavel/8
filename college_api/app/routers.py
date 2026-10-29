from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from . import schemas, services
from .database import get_db


def crud_router(path: str, tag: str, service_cls, in_schema, out_schema, what: str) -> APIRouter:
    """Фабрика контроллеров: 5 стандартных CRUD-эндпоинтов с описанием для Swagger."""
    router = APIRouter(prefix=f"/api/{path}", tags=[tag])

    def get_service(db: Session = Depends(get_db)):
        return service_cls(db)

    @router.get("", response_model=list[out_schema], summary=f"Список: {what}")
    def list_items(s=Depends(get_service)):
        return s.list()

    @router.get("/{item_id}", response_model=out_schema, summary=f"Получить: {what} по id",
                responses={404: {"description": "Не найдено"}})
    def get_item(item_id: int, s=Depends(get_service)):
        return s.get(item_id)

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED,
                 summary=f"Создать: {what}",
                 responses={400: {"description": "Ошибка валидации"}, 409: {"description": "Дубликат"}})
    def create_item(data: in_schema, s=Depends(get_service)):
        return s.create(data.model_dump())

    @router.put("/{item_id}", response_model=out_schema, summary=f"Обновить: {what}",
                responses={400: {"description": "Ошибка валидации"}, 404: {"description": "Не найдено"}})
    def update_item(item_id: int, data: in_schema, s=Depends(get_service)):
        return s.update(item_id, data.model_dump())

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary=f"Удалить: {what}",
                   responses={404: {"description": "Не найдено"}, 409: {"description": "Есть связанные записи"}})
    def delete_item(item_id: int, s=Depends(get_service)):
        s.delete(item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


groups = crud_router("groups", "Группы", services.GroupService, schemas.GroupIn, schemas.GroupOut, "группа")
teachers = crud_router("teachers", "Преподаватели", services.TeacherService, schemas.TeacherIn, schemas.TeacherOut, "преподаватель")
subjects = crud_router("subjects", "Предметы", services.SubjectService, schemas.SubjectIn, schemas.SubjectOut, "предмет")
students = crud_router("students", "Студенты", services.StudentService, schemas.StudentIn, schemas.StudentOut, "студент")

# --- Стипендии (вариант 4). Маршрут /high объявлен ДО /{item_id}, иначе "high" будет принят за id.
scholarships = APIRouter(prefix="/api/scholarships", tags=["Стипендии (вариант 4)"])


def _svc(db: Session = Depends(get_db)):
    return services.ScholarshipService(db)


@scholarships.get("/high", response_model=list[schemas.HighScholarshipOut],
                  summary="Студенты на повышенной стипендии",
                  description="Возвращает студентов, у которых нет троек и посещаемость 100%. "
                              "Можно отфильтровать по группе и семестру.")
def high_scholarships(group_id: int | None = Query(None, description="id группы"),
                      semester: str | None = Query(None, pattern=r"^\d{4}/[12]$", description="Например 2026/1"),
                      s: services.ScholarshipService = Depends(_svc)):
    return s.list_high(group_id, semester)


_crud = crud_router("scholarships", "Стипендии (вариант 4)", services.ScholarshipService,
                    schemas.ScholarshipIn, schemas.ScholarshipOut, "стипендия")
# Переносим CRUD-маршруты в тот же роутер после /high
for r in _crud.routes:
    scholarships.routes.append(r)
