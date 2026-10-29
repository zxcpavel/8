from datetime import date
from pydantic import BaseModel, ConfigDict, Field

FIO = r"^[А-ЯЁA-Z][а-яёa-z-]+(\s[А-ЯЁA-Z][а-яёa-z-]+){1,2}$"
EMAIL = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Group
class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=50, examples=["454"])


class GroupOut(GroupIn, ORM):
    id: int


# ---- Teacher
class TeacherIn(BaseModel):
    full_name: str = Field(pattern=FIO, examples=["Петров Пётр Петрович"])
    email: str = Field(pattern=EMAIL, examples=["petrov@example.com"])


class TeacherOut(TeacherIn, ORM):
    id: int


# ---- Subject
class SubjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=150, examples=["Веб-аудит"])
    teacher_id: int | None = None


class SubjectOut(SubjectIn, ORM):
    id: int


# ---- Student
class StudentIn(BaseModel):
    full_name: str = Field(pattern=FIO, examples=["Иванов Иван Иванович"])
    email: str = Field(pattern=EMAIL, examples=["ivanov@example.com"])
    birth_date: date
    group_id: int


class StudentOut(StudentIn, ORM):
    id: int


# ---- Scholarship (вариант 4)
class ScholarshipIn(BaseModel):
    student_id: int
    semester: str = Field(pattern=r"^\d{4}/[12]$", examples=["2026/1"], description="Формат ГГГГ/1 или ГГГГ/2")
    attendance_percent: float = Field(ge=0, le=100, examples=[100])
    threes_count: int = Field(ge=0, examples=[0], description="Количество оценок «3» за семестр")


class ScholarshipOut(ScholarshipIn, ORM):
    id: int
    kind: str = Field(description="regular — обычная, high — повышенная")
    amount: float


class HighScholarshipOut(BaseModel):
    student_id: int
    full_name: str
    group: str
    semester: str
    attendance_percent: float
    threes_count: int
    amount: float
