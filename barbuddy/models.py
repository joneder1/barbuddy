from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

import datetime

class User(Base):
    __tablename__ = "users"
    
    #one to many relationship with a cocktail
    id = Column(Integer, primary_key=True)
    username = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    #establish relationship with Cocktail
    cocktails = relationship("Cocktail", backref="author")
    def as_dictionary(self):
        user = {
            "id": self.id,
            "username": self.username
        }    
        return user
    
class Cocktail(Base):
    __tablename__ = "cocktails"
    
    id = Column(Integer, primary_key=True)
    cocktailname = Column(String(128))
    description = Column(String(1024))
    location = Column(String(128))
    rating = Column(Integer)
    #datetime = Column(DateTime, default=datetime.datetime.now)
    #users can have multiple cocktails
    author_id = Column(Integer, ForeignKey('users.id'))
    
    def as_dictionary(self):
        cocktail = {
            "id": self.id,
            "cocktailname": self.cocktailname,
            "description": self.description,
            "location": self.location,
            "rating": self.rating,
            #"datetime": self.datetime,
            "author_id": self.author_id
        }
        return cocktail