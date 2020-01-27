# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root@/Eventos?host=localhost?port=3306')
#TODO: Change connector link
Session = sessionmaker(bind=engine)

Base = declarative_base()