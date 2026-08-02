from unittest import skip

from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String, unique = True)
    category: Mapped[str] = mapped_column(String, nullable = False)
    size: Mapped[int] = mapped_column(BigInteger, nullable = False)
    
