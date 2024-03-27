from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from models.dams import Dams, DamData


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


# dam_data = dams_data_to_dict_list(dam_name="uMzingwane Dam")
# #"uMzingwane Dam"
# print(dam_data)


def dams_dicts(dams):
    dams_list = []
    for dam in dams:
        dams_dict = {}
        for columns in dam.__table__.columns:
            dams_dict[columns.name] = getattr(dam, columns.name)
        dams_list.append(dams_dict)
    return dams_list



# session.commit()
# session.rollback()

#dam_name="uMzingwane Dam"