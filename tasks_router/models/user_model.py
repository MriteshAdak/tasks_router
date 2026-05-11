import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String

from tasks_router.database.initiate_db import Base

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    # password: Mapped[str] = mapped_column(String, nullable=False)