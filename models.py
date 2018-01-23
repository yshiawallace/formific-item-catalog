import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Medium(Base):
    __tablename__ = 'medium'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class ArtItem(Base):
    __tablename__ = 'art_item'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    material = Column(String)
    image_url = Column(String)
    video_url = Column(String)
    year = Column(String)
    medium_id = Column(Integer, ForeignKey('medium.id'))
    medium = relationship(Medium)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'material': self.material,
            'image url': self.image_url,
            'video url': self.video_url,
            'year': self.year,
            'medium_id': self.medium.id
        }


engine = create_engine('sqlite:///catalog/formific.db')


Base.metadata.create_all(engine)