from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models import Base
from user import User
from medium import Medium


class ArtItem(Base):
    """Define ArtItem table"""

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
        """Return JSON for ArtItem data"""
        return {
            'name': self.name,
            'description': self.description,
            'material': self.material,
            'image url': self.image_url,
            'video url': self.video_url,
            'year': self.year,
            'medium_id': self.medium.id
        }