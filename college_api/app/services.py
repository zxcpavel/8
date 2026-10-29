from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .errors import NotFoundError, BusinessError
from .repositories import Repository

# Размеры стипендий (условные значения для учебного проекта)
REGULAR_AMOUNT = 2000.0
HIGH_AMOUNT = 3500.0


class CrudService:
    """Слой бизнес-логики: общий CRUD + проверка существования связанных записей."""
    model = None
    entity_name = ""
    refs: dict = {}  # поле -> модель, на которую оно ссылается

    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db, self.model)

    def _check_refs(self, data: dict):
        for field, ref_model in self.refs.items():
            ref_id = data.get(field)
            if ref_id is not None and self.db.get(ref_model, ref_id) is None:
                raise BusinessError(f"{ref_model.__name__} с id={ref_id} не существует (поле {field})")

    def _prepare(self, data: dict) -> dict:
        return data

    def list(self):
        return self.repo.list()

    def get(self, id: int):
        obj = self.repo.get(id)
        if obj is None:
            raise NotFoundError(self.entity_name, id)
        return obj

    def create(self, data: dict):
        self._check_refs(data)
        return self.repo.add(self._prepare(data))

    def update(self, id: int, data: dict):
        obj = self.get(id)
        self._check_refs(data)
        return self.repo.update(obj, self._prepare(data))

    def delete(self, id: int):
        self.repo.delete(self.get(id))


class GroupService(CrudService):
    model, entity_name = models.Group, "Группа"


class TeacherService(CrudService):
    model, entity_name = models.Teacher, "Преподаватель"


class SubjectService(CrudService):
    model, entity_name = models.Subject, "Предмет"
    refs = {"teacher_id": models.Teacher}


class StudentService(CrudService):
    model, entity_name = models.Student, "Студент"
    refs = {"group_id": models.Group}


class ScholarshipService(CrudService):
    model, entity_name = models.Scholarship, "Стипендия"
    refs = {"student_id": models.Student}

    @staticmethod
    def is_high(attendance_percent: float, threes_count: int) -> bool:
        """БИЗНЕС-ПРАВИЛО ВАРИАНТА 4:
        повышенная стипендия, если нет троек И посещаемость 100%."""
        return threes_count == 0 and attendance_percent == 100

    def _prepare(self, data: dict) -> dict:
        high = self.is_high(data["attendance_percent"], data["threes_count"])
        data["kind"] = "high" if high else "regular"
        data["amount"] = HIGH_AMOUNT if high else REGULAR_AMOUNT
        return data

    def list_high(self, group_id: int | None = None, semester: str | None = None):
        """Специфический GET: студенты на повышенной стипендии."""
        q = (
            select(models.Scholarship, models.Student, models.Group)
            .join(models.Student, models.Scholarship.student_id == models.Student.id)
            .join(models.Group, models.Student.group_id == models.Group.id)
            .where(models.Scholarship.kind == "high")
            .order_by(models.Group.name, models.Student.full_name)
        )
        if group_id is not None:
            q = q.where(models.Student.group_id == group_id)
        if semester is not None:
            q = q.where(models.Scholarship.semester == semester)
        return [
            {
                "student_id": st.id, "full_name": st.full_name, "group": gr.name,
                "semester": sc.semester, "attendance_percent": sc.attendance_percent,
                "threes_count": sc.threes_count, "amount": sc.amount,
            }
            for sc, st, gr in self.db.execute(q)
        ]
