from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, DateTime

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = 'task'
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default='todo', nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)