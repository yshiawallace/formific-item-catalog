from sqlalchemy import Column, ForeignKey, Integer, String
from models import Base


class User(Base):
    """Define User table"""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))