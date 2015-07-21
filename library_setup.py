from sqlalchemy import (
    Column, ForeignKey, Integer, String
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

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
    patronID = Column(Integer, ForeignKey('patrons.id'))
    patrons = relationship(Patrons)
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

engine = create_engine('sqlite:///theArchives.db')

Base.metadata.create_all(engine)
