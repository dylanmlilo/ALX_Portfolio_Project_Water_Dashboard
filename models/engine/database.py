import pandas as pd
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
from dotenv import load_dotenv

load_dotenv()

db_connection_string = os.getenv("db_connection_string")


engine = create_engine(db_connection_string)

Session = sessionmaker(bind=engine)

session = Session()

def dams_data_to_dict_list(dam_name=None, dam_id=None):
    """
    Convert SQLAlchemy query results into a list of dictionaries.
    Exclude the _sa_instance_state attribute.

    Args:
        dam_name (str, optional): Filter results by dam name. Defaults to None.
        dam_id (int, optional): Filter results by dam ID. Defaults to None.

    Returns:
        list: A list of dictionaries containing dam data.
    """
    try:
        query = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id)
    except:
        session.rollback()
    finally:
        session.close()

    # Apply filters based on arguments
    if dam_name:
        try:
            query = query.filter(Dams.dam_name == dam_name)
        except:
            session.rollback()
        finally:
            session.close()
    elif dam_id:
        try:
            query = query.filter(DamData.dam_id == dam_id)
        except:
            session.rollback()
        finally:
            session.close()

    dams_data = query.all()
    result_list = []
    for row in dams_data:
        result_dict = {}
        for table_obj in row:
            for column in table_obj.__table__.columns:
                if column.name != '_sa_instance_state':
                    result_dict[column.name] = getattr(table_obj, column.name)
        result_list.append(result_dict)

    sorted_result_list = sorted(result_list, key=lambda x: x["id"])
    return sorted_result_list


def reservoir_data_to_dict_list(reservoir_name=None, reservoir_id=None):
    """
    Convert SQLAlchemy query results for reservoir_data into a list of dictionaries.
    Exclude the _sa_instance_state attribute.

    Args:
        reservoir_name (str, optional): Filter results by reservoir name. Defaults to None.
        reservoir_id (int, optional): Filter results by reservoir ID. Defaults to None.

    Returns:
        list: A list of dictionaries containing reservoir data.
    """
    try:
        query = session.query(Reservoirs, ReservoirData).join(ReservoirData, Reservoirs.id == ReservoirData.reservoir_id)
    except:
        session.rollback()
    finally:
        session.close()

    if reservoir_name:
        try:
            query = query.filter(Reservoirs.reservoir_name == reservoir_name)
        except:
            session.rollback()
        finally:
            session.close()
    elif reservoir_id:
        try:
            query = query.filter(ReservoirData.reservoir_id == reservoir_id)
        except:
            session.rollback()
        finally:
                session.close()

    reservoir_data = query.all()
    result_list = []
    for row in reservoir_data:
        result_dict = {}
        for table_obj in row:
            for column in table_obj.__table__.columns:
                if column.name != '_sa_instance_state':
                    result_dict[column.name] = getattr(table_obj, column.name)
        result_list.append(result_dict)

    sorted_result_list = sorted(result_list, key=lambda x: x["id"])
    return sorted_result_list


def current_reservoir_levels(reservoir_name):
    try:
        current_level = (
            session.query(ReservoirData.reservoir_level)
            .join(Reservoirs, Reservoirs.id == ReservoirData.reservoir_id)
            .filter(Reservoirs.reservoir_name == reservoir_name)
            .order_by(ReservoirData.date.desc())
            .first()
        )
    except:
        session.rollback()
    finally:
        session.close()
    if current_level is not None:
        return current_level[0]
    else:
        return None

def current_dam_percentages(dam_name):
    try:
        current_dam_percentage = session.query(DamData.dam_percentage) \
                                    .join(Dams, Dams.id == DamData.dam_id) \
                                    .filter(Dams.dam_name == dam_name) \
                                    .order_by(DamData.date.desc()) \
                                    .first()
    except:
        session.rollback()
    
    finally:
        session.close()
                                 
    if current_dam_percentage is not None:
        current_dam_percentage = current_dam_percentage[0]
                                 
    return current_dam_percentage
