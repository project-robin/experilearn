from fastapi.testclient import TestClient
from app import app

c = TestClient(app)

def _instr():
    return c.post("/auth/login", json={"email": "instructor@experilearn.com", "password": "Instructor@123"}).json()["token"]

def test_list_courses_paginated():
    r = c.get("/courses")
    assert r.status_code == 200
    b = r.json()
    assert "items" in b and "total" in b and "page" in b
    assert b["total"] >= 10

def test_search_filter():
    r = c.get("/courses", params={"q": "Robotics", "category": "Robotics"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1

def test_create_course_module_progress_enroll():
    tok = _instr()
    h = {"Authorization": f"Bearer {tok}"}
    r = c.post("/courses", json={"title": "E2E Course", "description": "d", "category": "Technology", "difficulty": "Beginner", "price": 10}, headers=h)
    assert r.status_code == 201
    cid = r.json()["id"]

    r = c.post(f"/courses/{cid}/modules", json={"title": "M1", "type": "Virtual Lab", "content": "do it"}, headers=h)
    assert r.status_code == 201
    mid = r.json()["id"]
    assert c.get(f"/courses/{cid}/modules").status_code == 200

    r = c.post(f"/modules/{mid}/quiz", json={"title": "Q", "questions": [{"q": "2+2?", "options": ["3", "4"], "answer": 1}]}, headers=h)
    assert r.status_code == 201

    stok = c.post("/auth/login", json={"email": "student@experilearn.com", "password": "Student@123"}).json()["token"]
    sh = {"Authorization": f"Bearer {stok}"}
    assert c.post(f"/enrollments/{cid}", headers=sh).status_code == 201
    assert c.get("/enrollments/my", headers=sh).status_code == 200

    r = c.post(f"/modules/{mid}/quiz/attempt", json={"answers": [1]}, headers=sh)
    assert r.status_code == 200 and r.json()["score"] == 100
    assert c.get(f"/progress/{cid}", headers=sh).json()["progress"] == 100

def test_analytics_and_export():
    tok = _instr()
    h = {"Authorization": f"Bearer {tok}"}
    assert c.get("/analytics/instructor", headers=h).status_code == 200
    xml = c.get("/courses/1/export/xml")
    assert xml.status_code == 200 and "<course" in xml.text
    pdf = c.get("/courses/1/export/pdf")
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"
