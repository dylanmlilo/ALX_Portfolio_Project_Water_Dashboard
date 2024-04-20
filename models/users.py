from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin

# Base.metadata.create_all(engine)
Base = declarative_base()


class Users(Base, UserMixin):
    """
    Represents a table for users with the following columns:
    - id (Integer): The primary key of the user.
    - name (String): The name of the user.
    - username (String): The username of the user (unique).
    - password (String): The password of the user.
    - email (String): The email of the user (unique).
    """
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(50), unique=True)
    password = Column(String(50))
    email = Column(String(50), unique=True)

    def __repr__(self):
        return "<Users(name='%s', username='%s', password='%s', email='%s')>" % (self.name, self.username, self.password, self.email)

