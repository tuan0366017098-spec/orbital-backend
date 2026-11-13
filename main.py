# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict

import models
from database import engine, SessionLocal

# Khởi tạo database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orbital Game Backend", version="1.0")

# --- CẤU HÌNH CORS (Cho phép Frontend gọi API thoải mái) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Có thể đổi thành domain cụ thể khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency lấy DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class GameSubmit(BaseModel):
    user_id: int
    seed: str
    final_score: float
    ending_type: str
    decisions: Dict[str, Any]  # Lưu chuỗi JSON các quyết định qua 12 quý[cite: 2]

# --- API ENDPOINTS ---

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """API Đăng ký tài khoản"""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    new_user = models.User(username=user.username, password_hash=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Đăng ký thành công", "user_id": new_user.id}

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """API Đăng nhập cơ bản"""
    db_user = db.query(models.User).filter(
        models.User.username == user.username,
        models.User.password_hash == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    
    return {
        "message": "Đăng nhập thành công",
        "user_id": db_user.id,
        "username": db_user.username
    }

@app.post("/api/game/submit")
def submit_game_result(data: GameSubmit, db: Session = Depends(get_db)):
    """API nhận kết quả ván chơi từ client lưu vào database"""
    new_session = models.GameSession(
        user_id=data.user_id,
        seed=data.seed,
        final_score=data.final_score,
        ending_type=data.ending_type,
        decisions=data.decisions
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"message": "Đã lưu kết quả ván chơi thành công", "session_id": new_session.id}

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """API lấy Bảng xếp hạng, sắp xếp điểm từ cao xuống thấp[cite: 2]"""
    top_sessions = (
        db.query(models.GameSession)
        .order_by(models.GameSession.final_score.desc())
        .limit(10)
        .all()
    )
    
    results = []
    for s in top_sessions:
        user = db.query(models.User).filter(models.User.id == s.user_id).first()
        username = user.username if user else "Unknown"
        results.append({
            "username": username,
            "final_score": s.final_score,
            "ending_type": s.ending_type,
            "seed": s.seed,
            "created_at": s.created_at
        })
    return results
