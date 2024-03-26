from flask import Flask, render_template, abort, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
from models.engine.database import results_to_dict_list, dams_dicts, session
from models.dams import Base, Dams, DamData, engine
from models.users import Users
from models.login import LoginForm
from datetime import datetime, timedelta
from dash import Dash, html, dcc, callback, Input, Output, dash_table
import pandas as pd
import json
import plotly
import plotly_express as px


app = Flask(__name__)
app.secret_key = 'Sherry123#'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(Users).get(int(user_id))


@app.route('/test_page', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def test_page():
    return render_template('test_page.html')

@app.route('/graph', strict_slashes=False)
def graph():
    dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    dam_data = results_to_dict_list(dams_data)
    df = pd.DataFrame(dam_data)
    fig1 = px.line(df, x = 'date', y = 'dam_reading', color='dam_name', title = "Date vs Dam Reading")
    
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("graph.html", graph1JSON=graph1JSON)


@app.route('/', strict_slashes=False)
def index():
    dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    dam_data = results_to_dict_list(dams_data)
    df = pd.DataFrame(dam_data)
    fig1 = px.area(df, x = 'date', y = 'dam_reading', color='dam_name', title = "Date vs Dam Reading")
    
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("home.html", graph1JSON=graph1JSON)
    # dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    # dams = results_to_dict_list(dams_data)
    # unique_dam_names = set(row['dam_name'] for row in dams)

    # # Create a dictionary with unique dam names as keys and empty lists as values
    # dam_data_by_dam_name = {dam_name: [] for dam_name in unique_dam_names}

    # # Loop through data again to populate the dictionary
    # for row in dams:
    #     dam_data_by_dam_name[row['dam_name']].append(row)  # Append data to the list

    # return render_template('home.html', dams=dam_data_by_dam_name)



@app.route('/<int:dam_id>', strict_slashes=False)
def dam(dam_id):
    dam_names = session.query(Dams).all()
    dams = dams_dicts(dam_names)
    dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    dam_data = results_to_dict_list(dams_data)
    
    # Find the specific dam by ID
    selected_dam = None
    for dam in dams:
        if dam['id'] == dam_id:
            selected_dam = dam
            break
    
    if selected_dam is None:
        abort(404)

    # Get today's date
    today_date = datetime.today()

    # Format the date string
    formatted_date = today_date.strftime('%d-%B-%Y')

    # Get percentages for today's reading (assuming date is a field in DamData)
    dam_percentage = session.query(Dams.dam_name, DamData.dam_percentage) \
                             .join(DamData, Dams.id == DamData.dam_id) \
                             .filter(DamData.date == today_date) \
                             .all()

    return render_template('dam_page.html', dam=dam, dam_data=dam_data, dam_percentage=dam_percentage, today_date=formatted_date)

@app.route('/login', strict_slashes=False, methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(Users).filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid username or password"
    return render_template('login.html', form=form)

@app.route('/logout', strict_slashes=False)
def logout():
    logout_user()
    return redirect(url_for('login'))

        

@app.route('/dam_data', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def dam_data():
    dams_data = session.query(Dams, DamData).join(DamData, Dams.id == DamData.dam_id).all()
    dam_data = results_to_dict_list(dams_data)

    return render_template('dam_data.html', dam_data_list=dam_data)

@app.route('/insert_dam_data', methods=['POST'])
def insert_dam_data():
    if request.method == 'POST':
        try:
            dam_id = request.form.get('dam_id')
            date = request.form.get('date')
            dam_reading = request.form.get('dam_reading')
            dam_percentage = request.form.get('dam_percentage')
            dam_volume = request.form.get('dam_volume')
            daily_inflow = request.form.get('daily_inflow')

            # Validation checks
            errors = []

            if not daily_inflow:
                daily_inflow = None
            else:
                try:
                    daily_inflow = float(daily_inflow)
                except ValueError:
                    errors.append("daily_inflows must be a valid number")

            if errors:
                return jsonify({'errors': errors}), 400

            new_dam_record = DamData(dam_id=dam_id, date=date, dam_reading=dam_reading, dam_percentage=dam_percentage, dam_volume=dam_volume, daily_inflow=daily_inflow)
            session.add(new_dam_record)
            session.commit()
            flash('Data inserted successfully')
            return redirect(url_for('dam_data'))

        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        
@app.route('/delete_dam_data/<int:dam_data_id>', methods=['GET', 'POST'])
@login_required
def delete_dam_data(dam_data_id):
    dam_data = session.query(DamData).filter_by(id=dam_data_id).first()
    if dam_data:
        session.delete(dam_data)
        session.commit()
        return redirect(url_for('dam_data'))
    else:
        return jsonify({'error': 'Data not found'}), 404
        
        
@app.route('/update_dam_data/<int:dam_data_id>', methods=['POST'])
@login_required
def update_dam_data(dam_data_id):
    if request.method == 'POST':
        try:
            dam_data = session.query(DamData).filter_by(id=dam_data_id).first()
            if dam_data:
                dam_data.dam_id = request.form.get('dam_id')
                dam_data.date = request.form.get('date')
                dam_data.dam_reading = request.form.get('dam_reading')
                dam_data.dam_percentage = request.form.get('dam_percentage')
                dam_data.dam_volume = request.form.get('dam_volume')
                dam_data.daily_inflow = request.form.get('daily_inflow')
                
                if not daily_inflow:
                    daily_inflow = None
                else:
                    try:
                        daily_inflow = float(daily_inflow)
                    except ValueError:
                        errors.append("daily_inflows must be a valid number")

            if errors:
                return jsonify({'errors': errors}), 400

                
                session.commit()
                flash('Data updated successfully')
                return redirect(url_for('dam_data'))
            else:
                return jsonify({'error': 'Dam data not found'}), 404

        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400

        
@app.route("/admin_dashboard", strict_slashes=False)
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")
        


if __name__ == '__main__':
    app.run(debug=True, port=3000)