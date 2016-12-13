import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name
        }


class BookItem(Base):
    __tablename__ = 'book_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    author = Column(String(100))
    year_published = Column(Integer)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'author': self.author,
            'year_published': self.year_published
        }


engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)
print "Database Created!"
