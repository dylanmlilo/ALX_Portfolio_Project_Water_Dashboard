from flask import Flask, render_template, abort, jsonify, request, redirect, url_for
from database import results_to_dict_list, dams_dicts, session
from models.dams import Base, Dams, DamData, engine

app = Flask(__name__)


@app.route('/', strict_slashes=False)
def index():
    dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    dams = results_to_dict_list(dams_data)
    unique_dam_names = set(row['dam_name'] for row in dams)

    # Create a dictionary with unique dam names as keys and empty lists as values
    dam_data_by_dam_name = {dam_name: [] for dam_name in unique_dam_names}

    # Loop through data again to populate the dictionary (optional)
    for row in dams:
        dam_data_by_dam_name[row['dam_name']].append(row)  # Append data to the list

    return render_template('home.html', dams=dam_data_by_dam_name)


@app.route('/<int:dam_id>', strict_slashes=False)
def dam(dam_id):
    dam_names =  session.query(Dams).all()
    dams = dams_dicts(dam_names)
    for dam in dams:
        if dam['id'] == dam_id:
            return render_template('dam_page.html', dam=dam)
    abort(404)


if __name__ == '__main__':
    app.run(debug=True)