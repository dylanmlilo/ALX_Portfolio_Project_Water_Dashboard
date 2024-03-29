from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
import pandas as pd


db_connection_string = "mysql+pymysql://root:Sherry123#@127.0.0.1/bcc_water_data?charset=utf8mb4"

engine = create_engine(db_connection_string)

Session = sessionmaker(bind=engine)

session = Session()


# dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()

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

    query = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id)

    # Apply filters based on arguments
    if dam_name:
        query = query.filter(Dams.dam_name == dam_name)
    elif dam_id:
        query = query.filter(DamData.dam_id == dam_id)

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

  query = session.query(Reservoirs, ReservoirData).join(ReservoirData, Reservoirs.id == ReservoirData.reservoir_id)

  # Apply filters based on arguments
  if reservoir_name:
      query = query.filter(Reservoirs.reservoir_name == reservoir_name)
  elif reservoir_id:
      query = query.filter(ReservoirData.reservoir_id == reservoir_id)

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



# dam_data = dams_data_to_dict_list(dam_name="uMzingwane Dam")
# #"uMzingwane Dam"
# print(dam_data)


# Get reservoir data using reservoir.id
# reservoir_data = reservoir_data_to_dict_list()
# df = pd.DataFrame(reservoir_data)
# print(df)





# session.commit()
# session.rollback()

#dam_name="uMzingwane Dam"