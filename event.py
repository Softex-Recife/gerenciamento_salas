# coding=utf-8

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship, backref

from base import Base


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    start = Column(DateTime)
    end = Column(DateTime)
    room = Column(String(15))
    phone = Column(String(15))
    emails = Column(String(150))
    password = Column(String(10))


    def __init__(self, id, name, start, end, room, phone, emails, pwd):
        self.id = id
        self.name = name
        self.start = start
        self.end = end
        self.room = room
        self.phone = phone
        self.emails = emails
        self.password = pwd
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "room": self.room,
            "phone": self.phone,
            "emails": self.emails,
            "password": self.password,
        }