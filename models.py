# models.py
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Lưu mật khẩu (nên mã hóa bcrypt sau)
    created_at = Column(DateTime, default=datetime.utcnow)

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    seed = Column(String)            # Mã seed của ván đấu
    final_score = Column(Float)      # Điểm số tổng kết (thang 100)
    ending_type = Column(String)     # Loại ending đạt được (vd: IPO, Phá sản...)[cite: 2]
    decisions = Column(JSON)         # Lưu toàn bộ lịch sử chọn thẻ/thế ngân sách qua các quý[cite: 2]
    created_at = Column(DateTime, default=datetime.utcnow)
