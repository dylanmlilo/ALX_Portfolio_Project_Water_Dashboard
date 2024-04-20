from sqlalchemy import Column, Integer, String, Float, Text, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Reservoirs(Base):
    """
    Represents a table for reservoirs with the following columns:
    - id (Integer): The primary key of the reservoir.
    - reservoir_name (String): The name of the reservoir.
    - critical_level (Float): The critical level of the reservoir.
    - max_level (Float): The maximum level of the reservoir.
    - design_volume (Float): The design volume of the reservoir.
    - reservoir_description (Text): The description of the reservoir.
    """
    
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
    """
    Represents a table for reservoir data with the following columns:
    - id (Integer): The primary key of the reservoir data.
    - reservoir_id (Integer): The foreign key of the reservoir.
    - date (Date): The date of the reservoir data.
    - reservoir_level (Float): The level of the reservoir.
    - reservoir_percentage (Float): The percentage of the reservoir.
    - reservoir_volume (Float): The volume of the reservoir.
    """
    
    __tablename__ = 'reservoir_data'

    id = Column(Integer, primary_key=True)
    reservoir_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    reservoir_level = Column(Float, nullable=False)
    reservoir_percentage = Column(Float, nullable=False)
    reservoir_volume = Column(Float)

    def __repr__(self):
        return f"<ReservoirData(id={self.id}, reservoir_id={self.reservoir_id}, date={self.date}, level_reading={self.reservoir_level}, reservoir_percentage={self.reservoir_percentage}, reservoir_volume={self.reservoir_volume})>"

