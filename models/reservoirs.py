from sqlalchemy import Column, Integer, String, Float, Text, Date, PrimaryKeyConstraint, DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Reservoirs(Base):
    __tablename__ = 'reservoirs'

    id = Column(Integer, primary_key=True)
    reservoir_name = Column(String(255), nullable=False)
    critical_level = Column(Float, nullable=False)
    max_level = Column(Float, nullable=False)
    design_volume = Column(Float, nullable=False)
    reservoir_description = Column(Text)

    def __repr__(self):
        return f"<Reservoir(id={self.id}, reservoir_name='{self.reservoir_name}')>"


class ReservoirData(Base):
    __tablename__ = 'reservoir_data'

    id = Column(Integer, primary_key=True)
    reservoir_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    reservoir_level = Column(Float, nullable=False)
    reservoir_percentage = Column(Float, nullable=False)
    reservoir_volume = Column(Float)

    def __repr__(self):
        return f"<ReservoirData(id={self.id}, reservoir_id={self.reservoir_id}, date={self.date}, level_reading={self.reservoir_level}, reservoir_percentage={self.reservoir_percentage}, reservoir_volume={self.reservoir_volume})>"

# Base.metadata.create_all(engine)
