from models.dams import Base, Dams, DamData, engine
from sqlalchemy.orm import sessionmaker


Session = sessionmaker(bind=engine)

session = Session()

def results_to_dict_list(results):
    """
    Convert SQLAlchemy query results into a list of dictionaries.
    Exclude the _sa_instance_state attribute.
    """
    result_list = []
    for row in results:
        result_dict = {}
        for table_obj in row:
            for column in table_obj.__table__.columns:
                if column.name != '_sa_instance_state':
                    result_dict[column.name] = getattr(table_obj, column.name)
        result_list.append(result_dict)
    return result_list


# dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()

def dams_dicts(dams):
    dams_list = []
    for dam in dams:
        dams_dict = {}
        for columns in dam.__table__.columns:
            dams_dict[columns.name] = getattr(dam, columns.name)
        dams_list.append(dams_dict)
    return dams_list

# dams =  session.query(Dams).all()



# dams_to_dicts = dams_dicts(dams)
# dam_data_to_dict = results_to_dict_list(dams_data)

# print(dams_to_dicts)
# print("----------")
# print(dam_data_to_dict[0])


