from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True) # Telegram User ID
    username = Column(String, nullable=True)
    country = Column(String, nullable=True)
    role = Column(String, default="user") # 'user', 'student', 'admin'
    coins = Column(Integer, default=0)
    level = Column(String, default="Новичок")
    referrer_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    progress = relationship("DayProgress", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False) # 'RUB' или 'BYN'
    status = Column(String, default="pending") # 'pending', 'approved', 'rejected'
    receipt = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")

class DayProgress(Base):
    __tablename__ = 'day_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    day_number = Column(Integer, nullable=False) # 1, 2, ..., 7
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False) # 'earn', 'spend'
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
