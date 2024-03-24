from sqlalchemy import create_engine, Column, Integer, String, Float, Date, PrimaryKeyConstraint, DECIMAL
from models.engine.database import Base, session, engine
from flask_login import UserMixin

# Base.metadata.create_all(engine)


class Users(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(50), unique=True)
    password = Column(String(50))
    email = Column(String(50), unique=True)

    def __repr__(self):
        return "<Users(name='%s', username='%s', password='%s', email='%s')>" % (self.name, self.username, self.password, self.email)


# # Create a new user object
# new_user = Users(name="Don", username="Nkomo", password="Sherry123#", email="donNkomo11@gmail.com")

# # Add the user to the session
# session.add(new_user)

# # Commit changes to the database
# session.commit()

# session.close()  # Close the session (optional but recommended)

# print("New user created successfully!")
