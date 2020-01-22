from datetime import datetime
from copy import deepcopy
from base import Session, engine, Base
from event import Event

class EventDAO:

    Base.metadata.create_all(engine)
        
    def __get_session(self):
        return Session()

    def __commit(self, session):
        session.commit()
        session.close()

    def create(self, event):
        session = self.__get_session()
        session.add(event)
        self.__commit(session)

    def read(self, room_name):
        session = self.__get_session()
        now = datetime.now()
        event = session.query(Event) \
            .filter(Event.start <= now) \
            .filter(Event.end > now) \
            .filter(Event.room == room_name) \
            .first()
        event = deepcopy(event)
        self.__commit(session)
        return event
        

    def update(self, event):
        session = self.__get_session()
        session.query(Event).filter(Event.id==event.id).update(event.to_dict())
        self.__commit(session)

    def delete(self, event):
        session = self.__get_session()
        session.query(Event).filter(Event.id==event.id).delete()
        self.__commit(session)
