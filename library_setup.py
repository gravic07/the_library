# The Library v1.0.0
# Grant Vickers - https://github.com/gravic07

from sqlalchemy import (
    Column, ForeignKey, Integer, String
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Table of all Patrons (users)
class Patrons(Base):
    __tablename__ = 'patrons'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))

class Collections(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(1000))
    patronID = Column(Integer, ForeignKey('patrons.id'))
    patrons = relationship(Patrons)
    collectionOfBooks = relationship('Books', cascade='all, delete-orphan')
    # Convert data into JSON format
    @property
    def serialize(self):
        '''Returns object data in serialized format
        '''
        return {
            'name' : self.name,
            'id'   : self.id,
        }

class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    author = Column(String(80))
    genre = Column(String(100))
    description = Column(String(1000))
    coverImage = Column(String(250))
    collectionID = Column(Integer, ForeignKey('collections.id'))
    patronID = Column(Integer, ForeignKey('patrons.id'))
    collections = relationship(Collections)
    patrons = relationship(Patrons)
    # Convert data into JSON format
    @property
    def serialize(self):
        '''Returns object data in serialized format
        '''
        return {
            'title'       : self.title,
            'author'      : self.author,
            'genre'       : self.genre,
            'description' : self.description,
            'coverImage'  : self.coverImage,
            'id'          : self.id,
        }


# localEngine for use locally; engine for use on Apache2 server
localEngine = create_engine('sqlite:///theArchive.db')
engine = create_engine('postgresql://catalog:catalog@localhost/theArchive')

# This engine is used in the application hosted on Heroku
# http://udacity-p3-the-library.herokuapp.com/
# engine = create_engine('postgres://ewcuvsjxbhzuce:lTxnaKjAsx3L5JVCsjN1NXrrnS@ec2-54-83-20-177.compute-1.amazonaws.com:5432/d6l2vgh7udooqv')
# Create all tables in the declarative base.
Base.metadata.create_all(localEngine)
