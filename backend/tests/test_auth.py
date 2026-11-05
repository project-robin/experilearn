from fastapi.testclient import TestClient
from app import app

c = TestClient(app)

def test_health():
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_register_and_login():
    r = c.post("/auth/register", json={"email": "new1@t.com", "password": "pw123456", "name": "New", "role": "STUDENT"})
    assert r.status_code == 201
    body = r.json()
    assert "token" in body and body["user"]["role"] == "STUDENT"

    r2 = c.post("/auth/login", json={"email": "new1@t.com", "password": "pw123456"})
    assert r2.status_code == 200
    tok = r2.json()["token"]

    r3 = c.get("/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert r3.status_code == 200
    assert r3.json()["email"] == "new1@t.com"

def test_demo_users_login():
    for email, pw in [("admin@experilearn.com", "Admin@123"), ("instructor@experilearn.com", "Instructor@123"), ("student@experilearn.com", "Student@123")]:
        r = c.post("/auth/login", json={"email": email, "password": pw})
        assert r.status_code == 200, email
        assert r.json()["user"]["email"] == email

def test_student_cannot_create_course():
    tok = c.post("/auth/login", json={"email": "student@experilearn.com", "password": "Student@123"}).json()["token"]
    r = c.post("/courses", json={"title": "X"}, headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 403
