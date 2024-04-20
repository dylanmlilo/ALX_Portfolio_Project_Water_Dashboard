from flask import Flask, render_template, abort, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models.engine.database import session, dams_data_to_dict_list, reservoir_data_to_dict_list, current_reservoir_levels, current_dam_percentages
from models.users import Users
from models.login import LoginForm
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
from models.plot_functions import today_date, plot_reservoir_level_charts, plot_dam_level_charts, plot_home_page_charts
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user object from the database based on the user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Users or None: The user object if found, None otherwise.
    """
    try:
        user = session.query(Users).get(int(user_id))
    except:
        session.rollback()
    finally:
        session.close()
    return user


@app.route('/login', strict_slashes=False, methods=['GET', 'POST'])
def login():
    """
    Renders the login page template and handles user login.

    Returns:
        flask.Response: The rendered login page template or a redirect
        to the admin dashboard.
    """
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = session.query(Users).filter_by(username=form.username.data).first()
        except:
            session.rollback()
        finally:
            session.close()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid username or password"
    return render_template('login.html', form=form)

@app.route('/logout', strict_slashes=False)
def logout():
    """
    Logs out the current user and redirects to the login page.

    Returns:
        flask.Response: A redirect response to the login page.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/', strict_slashes=False)
def index():
    """
    Renders the home page template with the necessary data and charts.

    Returns:
        flask.Response: The rendered home page template.
    """
    graph1JSON, graph2JSON, gauge_reservoir_json, gauge_dam_json = plot_home_page_charts()
    
    date = today_date()
    
    return render_template("home.html", graph1JSON=graph1JSON,
                           graph2JSON=graph2JSON,gauge_dam_json=gauge_dam_json,
                           gauge_reservoir_json=gauge_reservoir_json, date=date)


@app.route('/about', strict_slashes=False)
def landing():
    """
    Renders the landing page template.

    Returns:
        flask.Response: The rendered landing page template.
    """
    return render_template("landing.html")


@app.route("/admin_dashboard", strict_slashes=False)
@login_required
def admin_dashboard():
    """
    Renders the admin dashboard page.

    Returns:
        flask.Response: The rendered admin dashboard template.
    """
    return render_template("admin_dashboard.html")
        

@app.route('/dams', strict_slashes=False)
def dams():
    """
    Renders the dams page template.

    Returns:
        flask.Response: The rendered dams page template.
    """
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
    try:
        dam = session.query(Dams).filter(Dams.dam_name == dam_name).first()

    except Exception as e:
        session.rollback()
        
    finally:
        session.close()
    
    if dam is None:
        abort(404)  # Dam not found

    # Get dam data using dam.id
    dam_data = dams_data_to_dict_list(dam_id=dam.id)
   
    formatted_date = today_date()
    
    critical_dam_percentage = 40
    current_dam_percentage = current_dam_percentages(dam_name)
    
    dam_graph1JSON, dam_graph2JSON, dam_graph3JSON = plot_dam_level_charts(dam_name) 
    
    return render_template('dam_page.html', dam=dam, dam_data=dam_data, 
                           today_date=formatted_date, critical_dam_percentage=critical_dam_percentage, 
                           current_dam_percentage=current_dam_percentage, dam_graph1JSON=dam_graph1JSON, 
                           dam_graph2JSON=dam_graph2JSON, dam_graph3JSON=dam_graph3JSON)
    

@app.route('/dam_data', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def dam_data():
    """
    Renders the dam data page template with the data for all dams.

    Returns:
        flask.Response: The rendered dam data page template.
    """
    dam_data = dams_data_to_dict_list()
    return render_template('dam_data.html', dam_data_list=dam_data)


@app.route('/insert_dam_data', methods=['POST'])
def insert_dam_data():
    """
    Inserts the dam data into the database and redirects to the dam data page.

    Returns:
        flask.Response: A redirect response to the dam data page or a JSON response with an error message.
    """
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
        
        finally:
            session.close()
        
@app.route('/delete_dam_data/<int:dam_data_id>', methods=['GET', 'POST'])
@login_required
def delete_dam_data(dam_data_id):
    """
    Deletes a specific dam data entry from the database and redirects to the dam data page.

    Args:
        dam_data_id (int): The ID of the dam data entry to be deleted.

    Returns:
        flask.Response: A redirect response to the dam data page or a JSON response if the data is not found.
    """
    try:
        dam_data = session.query(DamData).filter_by(id=dam_data_id).first()
    except:
        session.rollback()
    finally:
        session.close()
        
    if dam_data:
        session.delete(dam_data)
        session.commit()
        return redirect(url_for('dam_data'))
    else:
        return jsonify({'error': 'Data not found'}), 404
        
        
@app.route('/update_dam_data/<int:dam_data_id>', methods=['POST'])
@login_required
def update_dam_data(dam_data_id):
    """
    Updates the dam data entry in the database with the provided data and
    redirects to the dam data page.

    Args:
        dam_data_id (int): The ID of the dam data entry to be updated.

    Returns:
        flask.Response: A redirect response to the dam data page or
        a JSON response with an error message.
    """
    if request.method == 'POST':
        try:
            daily_inflow = None
            dam_data = session.query(DamData).filter_by(id=dam_data_id).first()
            if dam_data:
                dam_data.dam_id = request.form.get('dam_id')
                dam_data.date = request.form.get('date')
                dam_data.dam_reading = request.form.get('dam_reading')
                dam_data.dam_percentage = request.form.get('dam_percentage')
                dam_data.dam_volume = request.form.get('dam_volume')
                daily_inflow = request.form.get('daily_inflow')

                errors = []

                if daily_inflow is None or daily_inflow == '':
                    dam_data.daily_inflow = None
                else:
                    try:
                       daily_inflow = float(daily_inflow)
                    except ValueError:
                       errors.append("daily_inflow must be a valid number")

                if errors:
                    return jsonify({'errors': errors}), 400
                
                dam_data.daily_inflow = daily_inflow

                session.commit()
                flash('Data updated successfully')
                return redirect(url_for('dam_data'))
            else:
                return jsonify({'error': 'Dam data not found'}), 404

        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        
        finally:
            session.close()

        
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
    try:
        reservoir = session.query(Reservoirs).filter(Reservoirs.reservoir_name == reservoir_name).first()
    except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
    finally:
        session.close()

    if reservoir is None:
        abort(404)  # Reservoir not found

    # Get reservoir data using reservoir.id
    reservoir_data = reservoir_data_to_dict_list(reservoir_id=reservoir.id)
    
    critical_reservoir_level = reservoir.critical_level
    
    level_graphJSON, volume_graphJSON = plot_reservoir_level_charts(reservoir_name)
    
    current_reservoir_level = current_reservoir_levels(reservoir_name)

    formatted_date = today_date()

    return render_template('reservoir_page.html', reservoir=reservoir,
        reservoir_data=reservoir_data, today_date=formatted_date,
        critical_reservoir_level=critical_reservoir_level,
        current_reservoir_level=current_reservoir_level,
        level_graphJSON=level_graphJSON, volume_graphJSON=volume_graphJSON
    )
    
    
@app.route('/reservoir_data', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def reservoir_data():
    """
    Renders the reservoir data page with the reservoir data list.

    Returns:
        flask.Response: The rendered HTML template with the reservoir data list.
    """
    reservoir_data = reservoir_data_to_dict_list()
    return render_template('reservoir_data.html', reservoir_data_list=reservoir_data)


@app.route('/insert_reservoir_data', methods=['POST'])
def insert_reservoir_data():
    """
    Inserts a new reservoir data record into the database based on
    the form input and redirects to the reservoir data page.

    Returns:
        flask.Response: A redirect response to the reservoir data page or
        a JSON response with an error message.
    """
    if request.method == 'POST':
        try:
            reservoir_id = request.form.get('reservoir_id')
            date = request.form.get('date')
            reservoir_level = request.form.get('reservoir_level')
            reservoir_percentage = request.form.get('reservoir_percentage')
            reservoir_volume = request.form.get('reservoir_volume')

            errors = []

            if not reservoir_volume:
                reservoir_volume = None
            else:
                try:
                    reservoir_volume = float(reservoir_volume)
                except ValueError:
                    errors.append("reservoir_volume must be a valid number")

            if errors:
                return jsonify({'errors': errors}), 400

            new_reservoir_record = ReservoirData(reservoir_id=reservoir_id, date=date,
                                     reservoir_level=reservoir_level,
                                     reservoir_percentage=reservoir_percentage,
                                     reservoir_volume=reservoir_volume)
            
            session.add(new_reservoir_record)
            session.commit()
            flash('Data inserted successfully')
            return redirect(url_for('reservoir_data'))

        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        
        finally:
            session.close()
        
@app.route('/update_reservoir_data/<int:reservoir_data_id>', methods=['POST'])
@login_required
def update_reservoir_data(reservoir_data_id):
    """
    Updates the reservoir data entry in the database with the provided
    data and redirects to the reservoir data page.

    Args:
        reservoir_data_id (int): The ID of the reservoir data entry to be updated.

    Returns:
        flask.Response: A redirect response to the reservoir data page or
        a JSON response with an error message.
    """
    if request.method == 'POST':
        try:
            reservoir_volume = None
            reservoir_data = session.query(ReservoirData).filter_by(id=reservoir_data_id).first()
            if reservoir_data:
                reservoir_data.reservoir_id = request.form.get('reservoir_id')
                reservoir_data.date = request.form.get('date')
                reservoir_data.reservoir_level = request.form.get('reservoir_level')
                reservoir_data.reservoir_percentage = request.form.get('reservoir_percentage')
                reservoir_volume = request.form.get('reservoir_volume')

                errors = []

                if reservoir_volume is None or reservoir_volume == '':
                    reservoir_data.reservoir_volume = None
                else:
                    try:
                       reservoir_volume = float(reservoir_volume)
                    except ValueError:
                       errors.append("reservoir_volume must be a valid number")

                if errors:
                    return jsonify({'errors': errors}), 400
                
                reservoir_data.reservoir_volume = reservoir_volume

                session.commit()
                flash('Data updated successfully')
                return redirect(url_for('reservoir_data'))
            else:
                return jsonify({'error': 'Reservoir data not found'}), 404

        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        
        finally:
            session.close()


@app.route("/SIVvsConsumption", strict_slashes=False, methods=['GET', 'POST'])
def SIVvsConsumption():
    """
    Renders the SIVvsConsumption.html template.

    Returns:
        flask.Response: The rendered HTML template.
    """
    return render_template("SIVvsConsumption.html")

@app.route("/ChemicalStockLevels", strict_slashes=False)
def ChemicalStockLevels():
    """
    Renders the ChemicalStockLevels.html template.

    Returns:
        flask.Response: The rendered HTML template.
    """
    return render_template("ChemicalStockLevels.html")

@app.route("/PumpingStatistics", strict_slashes=False)
def PumpingStatistics():
    """
    Renders the PumpingStatistics.html template.

    Returns:
        flask.Response: The rendered HTML template.
    """
    return render_template("PumpingStatistics.html")

               
if __name__ == '__main__':
    app.run(debug=True)