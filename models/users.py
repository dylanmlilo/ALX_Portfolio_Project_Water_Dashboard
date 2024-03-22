import sqlalchemy
from sqlalchemy import create_engine,  Column, Integer, String, Float, Date, PrimaryKeyConstraint, DECIMAL
from sqlalchemy.orm import declarative_base


db_connection_string = "mysql+pymysql://root:Sherry123#@127.0.0.1/bcc_water_data?charset=utf8mb4"

engine = create_engine(db_connection_string)


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    email = Column(String(50))
    
    def __repr__(self):
        return "<Users(username='%s', password='%s', email='%s')>" % (self.username, self.password, self.email)
    
Base.metadata.create_all(engine)