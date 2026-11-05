import io, os
from datetime import datetime, timedelta
from typing import Optional
from xml.etree import ElementTree as ET

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./experilearn.db")
SECRET = os.getenv("SECRET", "dev-secret-change-me")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, default="")
    role = Column(String, default="STUDENT")  # STUDENT | INSTRUCTOR | ADMIN
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, default="Technology")  # Science, Technology, Robotics, Business, Design
    difficulty = Column(String, default="Beginner")  # Beginner, Intermediate, Advanced
    price = Column(Float, default=0)
    thumbnail = Column(String, default="")
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, default="Video Lesson")  # Virtual Lab, Simulation, Case Study, DIY Project, Video Lesson, Quiz
    content = Column(String, default="")
    order = Column(Integer, default=0)
    course = relationship("Course", back_populates="modules")
    quiz = relationship("Quiz", back_populates="module", uselist=False, cascade="all, delete-orphan")


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), unique=True, nullable=False)
    title = Column(String, default="")
    questions = Column(JSON, default=list)  # [{q, options[], answer:int}]
    module = relationship("Module", back_populates="quiz")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    percent = Column(Float, default=0)
    completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    user = relationship("User", back_populates="progress")


Base.metadata.create_all(engine)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str = ""
    role: str = "STUDENT"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    role: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


class UpdateProfileIn(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class CourseIn(BaseModel):
    title: str
    description: str = ""
    category: str = "Technology"
    difficulty: str = "Beginner"
    price: float = 0
    thumbnail: str = ""


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    price: float
    thumbnail: str
    instructor_id: Optional[int] = None


class ModuleIn(BaseModel):
    title: str
    type: str = "Video Lesson"
    content: str = ""
    order: int = 0


class ModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    title: str
    type: str
    content: str
    order: int


class QuizIn(BaseModel):
    title: str
    questions: list[dict] = []


class AttemptIn(BaseModel):
    answers: list[int] = []


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_token(u: User):
    return jwt.encode({"sub": str(u.id), "role": u.role, "exp": datetime.utcnow() + timedelta(days=7)}, SECRET)


bearer = HTTPBearer(auto_error=False)


def current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer), db: Session = Depends(get_db)):
    if not creds:
        raise HTTPException(401, "login required")
    try:
        sub = jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])["sub"]
    except Exception:
        raise HTTPException(401, "bad token")
    user = db.get(User, int(sub))
    if not user:
        raise HTTPException(401, "bad token")
    return user


def require_role(*roles):
    def check(user: User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, f"role required: {roles}")
        return user
    return check


def course_percent(db: Session, user_id: int, course: Course) -> float:
    if not course.modules:
        return 0.0
    done = 0
    for m in course.modules:
        p = db.query(Progress).filter(Progress.user_id == user_id, Progress.module_id == m.id).first()
        if p and (p.completed or p.percent >= 100):
            done += 1
    return round(done / len(course.modules) * 100, 1)


app = FastAPI(title="ExperiLearn")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(HTTPException)
async def http_errors(_, exc: HTTPException):
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled(_, exc: Exception):
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": f"internal error: {exc}"}, status_code=500)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Auth ---
@app.post("/auth/register", status_code=201, response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if body.role not in ("STUDENT", "INSTRUCTOR", "ADMIN"):
        raise HTTPException(400, "role must be STUDENT, INSTRUCTOR or ADMIN")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "email taken")
    u = User(email=body.email, name=body.name, role=body.role,
             password_hash=bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode())
    db.add(u); db.commit(); db.refresh(u)
    return {"token": make_token(u), "user": u}


@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not bcrypt.checkpw(body.password.encode(), u.password_hash.encode()):
        raise HTTPException(401, "bad credentials")
    return {"token": make_token(u), "user": u}


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


# --- Users ---
@app.get("/users/{uid}", response_model=UserOut)
def get_user(uid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "ADMIN" and user.id != uid:
        raise HTTPException(403, "admin only")
    target = db.get(User, uid)
    if not target:
        raise HTTPException(404, "not found")
    return target


@app.put("/users/{uid}", response_model=UserOut)
def update_user(uid: int, body: UpdateProfileIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "ADMIN" and user.id != uid:
        raise HTTPException(403, "admin only")
    target = db.get(User, uid)
    if not target:
        raise HTTPException(404, "not found")
    if body.name is not None:
        target.name = body.name
    if body.role is not None:
        if user.role != "ADMIN":
            raise HTTPException(403, "only admin changes role")
        target.role = body.role
    db.commit(); db.refresh(target)
    return target


@app.delete("/users/{uid}")
def delete_user(uid: int, user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    target = db.get(User, uid)
    if not target:
        raise HTTPException(404, "not found")
    db.delete(target); db.commit()
    return {"deleted": uid}


@app.get("/admin/users")
def list_users(user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    return db.query(User).all()


# --- Courses ---
@app.get("/courses")
def list_courses(q: str = "", category: str = "", difficulty: str = "", page: int = 1, size: int = 20,
                 db: Session = Depends(get_db)):
    query = db.query(Course)
    if q:
        query = query.filter(Course.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(Course.category == category)
    if difficulty:
        query = query.filter(Course.difficulty == difficulty)
    total = query.count()
    out = [c for c in query.offset((page - 1) * size).limit(size).all()]
    return {"items": out, "total": total, "page": page, "size": size}


@app.post("/courses", status_code=201)
def create_course(body: CourseIn, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    c = Course(**body.model_dump(), instructor_id=user.id)
    db.add(c); db.commit(); db.refresh(c)
    return c


@app.get("/courses/{cid}")
def get_course(cid: int, db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "not found")
    return c


@app.put("/courses/{cid}")
def update_course(cid: int, body: CourseIn, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "not found")
    if user.role != "ADMIN" and c.instructor_id != user.id:
        raise HTTPException(403, "not your course")
    for k, v in body.model_dump().items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c


@app.delete("/courses/{cid}")
def delete_course(cid: int, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "not found")
    if user.role != "ADMIN" and c.instructor_id != user.id:
        raise HTTPException(403, "not your course")
    db.delete(c); db.commit()
    return {"deleted": cid}


# --- Modules ---
@app.get("/courses/{cid}/modules")
def list_modules(cid: int, db: Session = Depends(get_db)):
    return db.query(Module).filter(Module.course_id == cid).order_by(Module.order).all()


@app.post("/courses/{cid}/modules", status_code=201)
def create_module(cid: int, body: ModuleIn, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    if not db.get(Course, cid):
        raise HTTPException(404, "course not found")
    m = Module(course_id=cid, **body.model_dump())
    db.add(m); db.commit(); db.refresh(m)
    return m


@app.get("/modules/{mid}")
def get_module(mid: int, db: Session = Depends(get_db)):
    m = db.get(Module, mid)
    if not m:
        raise HTTPException(404, "not found")
    return m


@app.put("/modules/{mid}")
def update_module(mid: int, body: ModuleIn, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    m = db.get(Module, mid)
    if not m:
        raise HTTPException(404, "not found")
    for k, v in body.model_dump().items():
        setattr(m, k, v)
    db.commit(); db.refresh(m)
    return m


@app.delete("/modules/{mid}")
def delete_module(mid: int, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    m = db.get(Module, mid)
    if not m:
        raise HTTPException(404, "not found")
    db.delete(m); db.commit()
    return {"deleted": mid}


# --- Quizzes ---
@app.post("/modules/{mid}/quiz", status_code=201)
def create_quiz(mid: int, body: QuizIn, user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    m = db.get(Module, mid)
    if not m:
        raise HTTPException(404, "module not found")
    q = Quiz(module_id=mid, title=body.title, questions=body.questions)
    db.add(q); db.commit(); db.refresh(q)
    return {"id": q.id, "title": q.title, "questions": q.questions}


@app.get("/modules/{mid}/quiz")
def get_quiz(mid: int, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.module_id == mid).first()
    if not q:
        raise HTTPException(404, "no quiz")
    return {"id": q.id, "title": q.title, "questions": q.questions}


@app.post("/modules/{mid}/quiz/attempt")
def attempt_quiz(mid: int, body: AttemptIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.module_id == mid).first()
    if not q:
        raise HTTPException(404, "no quiz")
    if len(body.answers) != len(q.questions):
        raise HTTPException(400, "answers length must match questions")
    correct = sum(1 for a, item in zip(body.answers, q.questions) if a == item.get("answer"))
    total = len(q.questions)
    score = round(correct / total * 100, 1) if total else 0
    p = db.query(Progress).filter(Progress.user_id == user.id, Progress.module_id == mid).first() or Progress(user_id=user.id, module_id=mid)
    p.score = score
    if score >= 80:
        p.percent = 100; p.completed = True
    db.add(p); db.commit()
    return {"score": score, "correct": correct, "total": total, "passed": score >= 80}


# --- Enrollments ---
@app.post("/enrollments/{cid}", status_code=201)
def enroll(cid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not db.get(Course, cid):
        raise HTTPException(404, "course not found")
    if db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.course_id == cid).first():
        raise HTTPException(400, "already enrolled")
    e = Enrollment(user_id=user.id, course_id=cid)
    db.add(e); db.commit(); db.refresh(e)
    return {"id": e.id, "course_id": cid}


@app.get("/enrollments/my")
def my_courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Enrollment).filter(Enrollment.user_id == user.id).all()
    out = []
    for e in rows:
        c = db.get(Course, e.course_id)
        out.append({"enrollment_id": e.id, "course": c, "progress": course_percent(db, user.id, c)})
    return out


# --- Progress ---
@app.post("/progress/{mid}/complete")
def complete_module(mid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    m = db.get(Module, mid)
    if not m:
        raise HTTPException(404, "module not found")
    p = db.query(Progress).filter(Progress.user_id == user.id, Progress.module_id == mid).first() or Progress(user_id=user.id, module_id=mid)
    p.percent = 100; p.completed = True
    db.add(p); db.commit()
    pct = course_percent(db, user.id, db.get(Course, m.course_id))
    cert = pct == 100
    return {"module_id": mid, "completed": True, "course_progress": pct,
            "certificate": f"ExperiLearn Certificate — {user.email} — Course {m.course_id} — 100%" if cert else None}


@app.get("/progress/{cid}")
def get_progress(cid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "course not found")
    return {"course_id": cid, "progress": course_percent(db, user.id, c)}


# --- Instructor analytics ---
@app.get("/analytics/instructor")
def analytics(user: User = Depends(require_role("INSTRUCTOR", "ADMIN")), db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.instructor_id == user.id).all() if user.role == "INSTRUCTOR" else db.query(Course).all()
    per_course = []
    total_enrollments = 0
    for c in courses:
        ens = db.query(Enrollment).filter(Enrollment.course_id == c.id).all()
        total_enrollments += len(ens)
        pcts = [course_percent(db, e.user_id, c) for e in ens]
        per_course.append({"course_id": c.id, "title": c.title, "enrollments": len(ens),
                           "avg_progress": round(sum(pcts) / len(pcts), 1) if pcts else 0})
    all_pcts = [p.percent for p in db.query(Progress).all()]
    return {"total_students": db.query(User).filter(User.role == "STUDENT").count(),
            "total_enrollments": total_enrollments,
            "avg_progress": round(sum(all_pcts) / len(all_pcts), 1) if all_pcts else 0,
            "per_course": per_course}


@app.get("/analytics/admin")
def admin_analytics(user: User = Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    return {"total_users": db.query(User).count(),
            "students": db.query(User).filter(User.role == "STUDENT").count(),
            "instructors": db.query(User).filter(User.role == "INSTRUCTOR").count(),
            "courses": db.query(Course).count(),
            "enrollments": db.query(Enrollment).count(),
            "modules": db.query(Module).count()}


# --- Legacy import/export ---
@app.get("/courses/{cid}/export/xml")
def export_xml(cid: int, db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "not found")
    root = ET.Element("course", {"id": str(c.id)})
    ET.SubElement(root, "title").text = c.title
    ET.SubElement(root, "description").text = c.description
    ET.SubElement(root, "category").text = c.category
    for m in c.modules:
        mod = ET.SubElement(root, "module", {"order": str(m.order)})
        ET.SubElement(mod, "title").text = m.title
        ET.SubElement(mod, "type").text = m.type
        ET.SubElement(mod, "content").text = m.content or ""
    return Response(ET.tostring(root, encoding="unicode"), media_type="application/xml",
                    headers={"Content-Disposition": f"attachment; filename=course-{cid}.xml"})


@app.get("/courses/{cid}/export/pdf")
def export_pdf(cid: int, db: Session = Depends(get_db)):
    c = db.get(Course, cid)
    if not c:
        raise HTTPException(404, "not found")
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=LETTER)
    p.drawString(72, 750, f"Progress report: {c.title}")
    y = 720
    for e in db.query(Enrollment).filter(Enrollment.course_id == cid).all():
        p.drawString(72, y, f"user {e.user_id}: {course_percent(db, e.user_id, c)}%")
        y -= 20
    p.showPage(); p.save()
    return Response(buf.getvalue(), media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=course-{cid}-report.pdf"})


@app.post("/admin/import/xml", status_code=201)
def import_xml(payload: str, user: User = Depends(require_role("ADMIN", "INSTRUCTOR")), db: Session = Depends(get_db)):
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        raise HTTPException(400, "invalid XML")
    title = root.findtext("title")
    if not title:
        raise HTTPException(400, "missing title")
    c = Course(title=title, description=root.findtext("description", ""), category=root.findtext("category", "Technology"),
               instructor_id=user.id)
    db.add(c); db.flush()
    for mod in root.findall("module"):
        db.add(Module(course_id=c.id, title=mod.findtext("title", ""), type=mod.findtext("type", "Video Lesson"),
                      content=mod.findtext("content", ""), order=int(mod.get("order", 0))))
    db.commit(); db.refresh(c)
    return {"id": c.id, "title": c.title}


def seed():
    db = SessionLocal()
    if db.query(User).count() >= 3:
        return
    def mk(email, pw, name, role):
        u = User(email=email, name=name, role=role,
                 password_hash=bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode())
        db.add(u); db.flush()
        return u
    admin = mk("admin@experilearn.com", "Admin@123", "Platform Admin", "ADMIN")
    instr = mk("instructor@experilearn.com", "Instructor@123", "Ivy Instructor", "INSTRUCTOR")
    student = mk("student@experilearn.com", "Student@123", "Sam Student", "STUDENT")

    courses = [
        ("Physics in Motion: Virtual Labs", "Hands-on mechanics — simulate collisions, gravity and friction in browser labs.", "Science", "Beginner", 49, "physics.png"),
        ("Data Structures & Algorithms by Building", "Build heaps, trees and graphs with guided DIY projects, then code them.", "Technology", "Intermediate", 79, "dsa.png"),
        ("Intro to Robotics: Build Your First Bot", "Assemble, program and test a line-follower bot step by step.", "Robotics", "Beginner", 99, "robotics.png"),
        ("Startup Finance: Numbers That Matter", "Case studies on runway, CAC and LTV with real company data.", "Business", "Intermediate", 89, "finance.png"),
        ("Design Thinking Studio", "Video lessons + DIY design sprints: empathy maps to final prototypes.", "Design", "Beginner", 69, "design.png"),
        ("Chemistry Simulations Lab", "Virtual titration, reaction simulations and lab safety drills.", "Science", "Intermediate", 59, "chem.png"),
        ("Python for Engineers", "Programs in Python for data, simulation and automation — lab driven.", "Technology", "Beginner", 79, "python.png"),
        ("Microcontrollers & IoT Prototyping", "DIY projects: sensors, actuators and cloud-connected prototypes.", "Robotics", "Advanced", 129, "iot.png"),
        ("Product Management Case Studies", "Analyse real product launches, prioritisation and roadmaps.", "Business", "Advanced", 119, "pm.png"),
        ("UI/UX Research & Prototyping", "Run usability tests and build interactive prototypes in-studio.", "Design", "Intermediate", 99, "ux.png"),
    ]
    types = ["Virtual Lab", "Simulation", "Case Study", "DIY Project", "Video Lesson", "Quiz"]
    for title, desc, cat, diff, price, thumb in courses:
        c = Course(title=title, description=desc, category=cat, difficulty=diff, price=price,
                   thumbnail=thumb, instructor_id=instr.id)
        db.add(c); db.flush()
        for i in range(1, 5):
            m = Module(course_id=c.id, title=f"{title} — Module {i}",
                       type=types[(i - 1) % len(types)],
                       content=f"Hands-on content for module {i} of {title}: complete the tasks, run the simulation, reflect and submit.",
                       order=i)
            db.add(m); db.flush()
            if i == 4:
                db.add(Quiz(module_id=m.id, title=f"{title} — Quiz",
                            questions=[{"q": f"Module {i} check {j}: correct answer?", "options": ["A", "B", "C"], "answer": j % 3} for j in range(3)]))
    # demo enrollment + progress so dashboards aren't empty
    e = Enrollment(user_id=student.id, course_id=db.query(Course).first().id)
    db.add(e); db.flush()
    m = db.query(Module).first()
    db.add(Progress(user_id=student.id, module_id=m.id, percent=100, completed=True))
    db.commit()
    db.close()


seed()
