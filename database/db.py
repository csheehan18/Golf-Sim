from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    
class Bay(Base):
    __tablename__ = 'bays'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), unique=True, nullable=False)
    
class Reservation(Base):
    __tablename__ = 'reservations'
    __table_args__ = (UniqueConstraint('user_id', 'date', 'timeslot', "bay_id"), )
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(String(50), nullable=False)
    timeslot = Column(String(5), nullable=False)
    bay_id  = Column(Integer, ForeignKey('bays.id'), nullable=False)

engine = create_engine('sqlite:///golf-sim.db')

