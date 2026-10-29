import os

os.environ["DATABASE_URL"] = "sqlite:///./test_college.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import engine
from app.models import Base
from app.services import ScholarshipService


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def make_student(c, email="ivanov@example.com", name="Иванов Иван Иванович"):
    gid = (c.post("/api/groups", json={"name": "454"}).json() or {}).get("id")
    if gid is None:
        gid = c.get("/api/groups").json()[0]["id"]
    r = c.post("/api/students", json={"full_name": name, "email": email,
                                      "birth_date": "2006-05-01", "group_id": gid})
    assert r.status_code == 201
    return r.json()["id"]


def test_rule():
    assert ScholarshipService.is_high(100, 0) is True
    assert ScholarshipService.is_high(99.9, 0) is False
    assert ScholarshipService.is_high(100, 1) is False


def test_high_list(client):
    s1 = make_student(client)
    s2 = make_student(client, "petrov@example.com", "Петров Пётр Петрович")
    client.post("/api/scholarships", json={"student_id": s1, "semester": "2026/1",
                                           "attendance_percent": 100, "threes_count": 0})
    client.post("/api/scholarships", json={"student_id": s2, "semester": "2026/1",
                                           "attendance_percent": 100, "threes_count": 2})
    r = client.get("/api/scholarships/high")
    assert r.status_code == 200
    assert [x["student_id"] for x in r.json()] == [s1]


def test_validation_400(client):
    r = client.post("/api/students", json={"full_name": "x", "email": "bad",
                                           "birth_date": "2006-05-01", "group_id": 1})
    assert r.status_code == 400


def test_404(client):
    assert client.get("/api/students/999").status_code == 404


def test_unknown_student_400(client):
    r = client.post("/api/scholarships", json={"student_id": 999, "semester": "2026/1",
                                               "attendance_percent": 100, "threes_count": 0})
    assert r.status_code == 400
