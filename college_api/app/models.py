from datetime import date
from sqlalchemy import ForeignKey, String, Float, Integer, Date, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"), nullable=True)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    birth_date: Mapped[date] = mapped_column(Date)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    group: Mapped[Group] = relationship()


class Scholarship(Base):
    """Доп. сущность варианта 4 — стипендия студента за семестр."""
    __tablename__ = "scholarships"
    __table_args__ = (UniqueConstraint("student_id", "semester", name="uq_student_semester"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    semester: Mapped[str] = mapped_column(String(10))          # например 2026/1
    attendance_percent: Mapped[float] = mapped_column(Float)   # 0..100
    threes_count: Mapped[int] = mapped_column(Integer)         # количество оценок «3»
    kind: Mapped[str] = mapped_column(String(10))              # regular | high (считается автоматически)
    amount: Mapped[float] = mapped_column(Float)
    student: Mapped[Student] = relationship()
