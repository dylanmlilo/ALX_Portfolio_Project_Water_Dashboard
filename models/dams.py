from sqlalchemy import Column, Integer, String, Float, Date, PrimaryKeyConstraint, DECIMAL
from models.engine.database import Base, engine, session


class Dams(Base):
    __tablename__ = 'dams'

    id = Column(Integer, primary_key=True)
    dam_name = Column(String(255), nullable=False)
    
    def __repr__(self):
            return f"<Dam(dam_name='{self.dam_name}')>"
    
class DamData(Base):
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

# Base.metadata.create_all(engine)