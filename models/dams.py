from sqlalchemy import Column, Integer, String, Float, Date, Text, PrimaryKeyConstraint, DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Dams(Base):
    """
    Represents a dam entity with attributes for dam name and description.

    Attributes:
        id (int): The primary key of the dam.
        dam_name (str): The name of the dam.
        dam_description (str): The description of the dam.
    """
    
    __tablename__ = 'dams'

    id = Column(Integer, primary_key=True)
    dam_name = Column(String(255), nullable=False)
    dam_description = Column(Text)
    
    def __repr__(self):
            return f"<Dam(dam_name='{self.dam_name}')>"
    
class DamData(Base):
    """
    Represents the data associated with a dam including readings,
    percentages, volumes, and daily inflow.

    Attributes:
        id (int): The primary key of the dam data.
        dam_id (int): The foreign key referencing the dam.
        date (Date): The date of the dam data entry.
        dam_reading (Decimal): The reading of the dam.
        dam_percentage (Decimal): The percentage of the dam level.
        dam_volume (Decimal): The volume of the dam.
        daily_inflow (Decimal): The daily inflow into the dam.
    """
    
    __tablename__ = 'dam_data'

    id = Column(Integer, primary_key=True)
    dam_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    dam_reading = Column(DECIMAL(10, 2), nullable=False)
    dam_percentage = Column(DECIMAL(5, 2), nullable=False)
    dam_volume = Column(DECIMAL(15, 2), nullable=False)
    daily_inflow = Column(DECIMAL(10, 2), nullable=False)
    
    def __repr__(self):
        return f"<DamData(dam_id={self.dam_id}, date={self.date}, dam_reading={self.dam_reading}, dam_percentage={self.dam_percentage}, dam_volume={self.dam_volume}, daily_inflow={self.daily_inflow})>"
