from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models import Base


class Medium(Base):
    """Define Medium table

    A medium is a category to which an item belongs.
    """
    __tablename__ = 'medium'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)