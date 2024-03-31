from flask import Flask, render_template, abort, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
from models.engine.database import dams_data_to_dict_list, reservoir_data_to_dict_list, session
from models.users import Users
from models.login import LoginForm
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
from datetime import datetime, timedelta
from dash import Dash, html, dcc, callback, Input, Output, dash_table
import pandas as pd
import json
import plotly
import plotly_express as px
import plotly.graph_objects as go


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
    dam_data = dams_data_to_dict_list()
    df = pd.DataFrame(dam_data)
    fig1 = px.line(df, x = 'date', y = 'dam_reading', color='dam_name', title = "Date vs Dam Reading")
    
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("graph.html", graph1JSON=graph1JSON)


@app.route('/', strict_slashes=False)
def index():
    dam_data = dams_data_to_dict_list()
    df = pd.DataFrame(dam_data)
    fig1 = px.area(df, x = 'date', y = 'dam_reading', color='dam_name',
                   labels={'x' : 'Date', 'y' : ' Dam Reading'}, title = "Dam Readings")
    
    reservoir_data = reservoir_data_to_dict_list()
    df = pd.DataFrame(reservoir_data)
    fig2 = px.area(df, x = 'date', y = 'reservoir_level', color='reservoir_name',
                   labels={'x' : 'Date', 'y' : ' Reservoir Level'}, title = "Reservoir Levels")
    
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("home.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON)


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

@app.route("/admin_dashboard", strict_slashes=False)
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")
        

@app.route('/dams', strict_slashes=False)
def dams():
    return render_template('dams_page.html')

@app.route('/dams/<string:dam_name>', strict_slashes=False)
def dam(dam_name):
    """
    Route to display dam details and data.

    Args:
        dam_name (str): Name of the dam to retrieve data for.

    Returns:
        template: Rendered dam_page.html template with dam details and data.
        404: If the specified dam is not found.
    """

    dam = session.query(Dams).filter(Dams.dam_name == dam_name).first()

    if dam is None:
        abort(404)  # Dam not found

    # Get dam data using dam.id
    dam_data = dams_data_to_dict_list(dam_id=dam.id)
    df = pd.DataFrame(dam_data)
    # Get the real value from the database
    critical_dam_percentage = 40
    dam_fig1 = px.area(df, x = 'date', y = 'dam_percentage',
                       labels={'x' : 'Date', 'y' : ' Dam Percentage'}, 
                       title = f"{dam.dam_name} Percentages")
    # Add a horizontal line for the critical_dam_percentage
    dam_fig1.add_hline(y=critical_dam_percentage, line_dash="dot",
                   line_color="red", annotation_text="Critical Dam Percentage")
    dam_graph1JSON = json.dumps(dam_fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    dam_fig2 = px.area(df, x = 'date', y = 'dam_reading',
                       labels={'x' : 'Date', 'y' : ' Dam Reading'},
                       title = f"{dam.dam_name} Readings")
    dam_graph2JSON = json.dumps(dam_fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    dam_fig3 = px.area(df, x = 'date', y = 'dam_volume',
                       labels={'x' : 'Date', 'y' : ' Dam Volume'}, 
                       title = f"{dam.dam_name} Volumes")
    dam_graph3JSON = json.dumps(dam_fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    today_date = datetime.today()

    formatted_date = today_date.strftime('%d-%B-%Y')
    
    current_dam_percentage = session.query(DamData.dam_percentage) \
                                 .join(Dams, Dams.id == DamData.dam_id) \
                                 .filter(Dams.dam_name == dam_name) \
                                 .order_by(DamData.date.desc()) \
                                 .first()

    if current_dam_percentage is not None:
        current_dam_percentage = current_dam_percentage[0] 
    
    return render_template('dam_page.html', dam=dam, dam_data=dam_data, 
                           today_date=formatted_date, critical_dam_percentage=critical_dam_percentage, 
                           current_dam_percentage=current_dam_percentage, dam_graph1JSON=dam_graph1JSON, 
                           dam_graph2JSON=dam_graph2JSON, dam_graph3JSON=dam_graph3JSON)
    

@app.route('/dam_data', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def dam_data():
    dam_data = dams_data_to_dict_list()
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
                
                errors = []
                
                if daily_inflow is None or daily_inflow == '':
                    daily_inflow = None
                else:
                    try:
                        daily_inflow = float(daily_inflow)
                    except ValueError:
                        errors.append("daily_inflow must be a valid number")


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
        
@app.route('/reservoirs/<string:reservoir_name>', strict_slashes=False)
def reservoir(reservoir_name):
    """
    Route to display reservoir details and data.

    Args:
        reservoir_name (str): Name of the reservoir to retrieve data for.

    Returns:
        template: Rendered reservoir_page.html template with reservoir details and data.
        404: If the specified reservoir is not found.
    """

    reservoir = session.query(Reservoirs).filter(Reservoirs.reservoir_name == reservoir_name).first()

    if reservoir is None:
        abort(404)  # Reservoir not found

    # Get reservoir data using reservoir.id
    reservoir_data = reservoir_data_to_dict_list(reservoir_id=reservoir.id)
    df = pd.DataFrame(reservoir_data)

    # Get critical reservoir percentage from the database
    critical_reservoir_level = reservoir.critical_level  # Assuming it's stored in the database

    # Generate graphs for levels, percentages, and volumes
    level_fig = px.area(df, x='date', y='reservoir_level',
                        labels={'x': 'Date', 'y': 'Reservoir Level'},
                        title=f"{reservoir.reservoir_name} Levels")
    level_fig.add_hline(y=critical_reservoir_level, line_dash="dot", line_color="red", annotation_text="Critical Level")
    level_graphJSON = json.dumps(level_fig, cls=plotly.utils.PlotlyJSONEncoder)

    volume_fig = px.area(df, x='date', y='reservoir_volume',
                         labels={'x': 'Date', 'y': 'Reservoir Volume'},
                         title=f"{reservoir.reservoir_name} Volumes")
    volume_graphJSON = json.dumps(volume_fig, cls=plotly.utils.PlotlyJSONEncoder)


    current_reservoir_level = (
        session.query(ReservoirData.reservoir_level)
        .join(Reservoirs, Reservoirs.id == ReservoirData.reservoir_id)
        .filter(Reservoirs.reservoir_name == reservoir_name)
        .order_by(ReservoirData.date.desc())
        .first()
    )
    current_reservoir_level = current_reservoir_level[0] if current_reservoir_level else None

    today_date = datetime.today().strftime('%d-%B-%Y')

    return render_template(
        'reservoir_page.html',
        reservoir=reservoir,
        reservoir_data=reservoir_data,
        today_date=today_date,
        critical_reservoir_level=critical_reservoir_level,
        current_reservoir_level=current_reservoir_level,
        level_graphJSON=level_graphJSON,
        volume_graphJSON=volume_graphJSON
    )
    
    
@app.route('/reservoir_data', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def reservoir_data():
    reservoir_data = reservoir_data_to_dict_list()
    return render_template('reservoir_data.html', reservoir_data_list=reservoir_data)

                
if __name__ == '__main__':
    app.run(debug=True, port=3000)