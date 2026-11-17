from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pwdlib import PasswordHash
from datetime import datetime
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from fastapi.staticfiles import StaticFiles
import os

# 1. НАСТРОЙКА БАЗЫ ДАННЫХ
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    applications = relationship("Application", back_populates="owner")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String)
    phone = Column(String)
    applications = relationship("Application", back_populates="teacher")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="applications")
    teacher = relationship("Teacher", back_populates="applications")

Base.metadata.create_all(bind=engine)

# 2. БЕЗОПАСНОСТЬ
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# 3. СЕРВЕР
app = FastAPI(title="Сайт кафедры")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Схемы данных
class TeacherResponse(BaseModel):
    id: int
    name: str
    subject: str
    phone: str
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class ApplicationCreate(BaseModel):
    teacher_id: int
    message: str
    username: str

# --- Обработчики ---

@app.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()

@app.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Педагог не найден")
    return teacher

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "Пользователь успешно создан"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"message": f"Добро пожаловать, {user.username}!"}

@app.post("/applications")
def create_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == app_data.username).first()
    if not user:
        hashed_pw = get_password_hash("123456")
        user = User(username=app_data.username, hashed_password=hashed_pw)
        db.add(user)
        db.commit()
        db.refresh(user)

    teacher_id = app_data.teacher_id if app_data.teacher_id else 1
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    new_app = Application(
        user_id=user.id,
        teacher_id=teacher.id,
        message=app_data.message
    )
    db.add(new_app)
    db.commit()
    return {"message": f"Заявка для {user.username} успешно создана!"}

@app.get("/my-applications")
def get_my_applications(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return []
        
    apps = db.query(Application).filter(Application.user_id == user.id).all()
    result = []
    for a in apps:
        result.append({
            "id": a.id,
            "message": a.message,
            "date": a.created_at.strftime("%d.%m.%Y %H:%M") if a.created_at else ""
        })
    return result

# ==========================================
# 4. НАПОЛНЕНИЕ БАЗЫ (15 записей)
# ==========================================
def fill_database():
    db = SessionLocal()
    if db.query(Teacher).count() == 0:
        teachers_data = [
            {"name": "Романова В.И.", "subject": "История", "phone": "+7 (900) 000-01-12"},
            {"name": "Воронцов Д.И.", "subject": "Математика", "phone": "+7 (900) 000-01-03"},
            {"name": "Громова А.С.", "subject": "Русский язык", "phone": "+7 (900) 000-01-02"},
            {"name": "Белова А.С.", "subject": "Литература", "phone": "+7 (900) 000-01-08"},
            {"name": "Алексеев М.О.", "subject": "История", "phone": "+7 (900) 000-01-01"},
            {"name": "Данилов А.В.", "subject": "Информатика", "phone": "+7 (900) 000-01-05"},
            {"name": "Егорова М.А.", "subject": "Физика", "phone": "+7 (900) 000-01-06"},
            {"name": "Зайцева О.Д.", "subject": "Литература", "phone": "+7 (900) 000-01-08"},
            {"name": "Крылов И.А.", "subject": "Экономика", "phone": "+7 (900) 000-01-09"},
            {"name": "Морозова С.Н.", "subject": "Физика", "phone": "+7 (900) 000-01-10"},
            {"name": "Жуков Н.Р.", "subject": "Высшая математика", "phone": "+7 (900) 000-01-07"},
            {"name": "Орлова П.Е.", "subject": "Экология", "phone": "+7 (900) 000-01-11"},
            {"name": "Соколов А.А.", "subject": "Программирование", "phone": "+7 (900) 000-01-15"},
            {"name": "Иванова Е.В.", "subject": "Экономика", "phone": "+7 (900) 000-01-16"},
            {"name": "Сидоров П.П.", "subject": "Информатика", "phone": "+7 (900) 000-01-17"},
        ]
        for t_data in teachers_data:
            teacher = Teacher(**t_data)
            db.add(teacher)
        db.commit()
        print("База данных успешно заполнена 15 педагогами!")
    db.close()

fill_database()

# ==========================================
# 5. РАЗДАЧА СТАТИКИ (В САМОМ КОНЦЕ!)
# ==========================================
# Это должно быть в самом конце, чтобы не перехватывать API!
if os.path.exists("index.html"):
    app.mount("/", StaticFiles(directory=".", html=True), name="static")