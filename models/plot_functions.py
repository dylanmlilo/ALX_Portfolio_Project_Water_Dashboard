from flask import abort
from dash import Dash, html, dcc, callback, Input, Output, dash_table
import pandas as pd
import json
import plotly
import plotly_express as px
import plotly.graph_objects as go
from models.engine.database import session, dams_data_to_dict_list, reservoir_data_to_dict_list
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
from datetime import datetime, timedelta



def today_date():
    today_date = datetime.today()

    formatted_date = today_date.strftime('%d-%B-%Y')
    
    return formatted_date

def plot_home_page_charts():
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
    
    # Define the reservoir levels
    reservoir_level = 75
    critical_reservoir_level = 50
    maximum_reservoir_level = 100
    
    # Create a figure for the speedometer plot
    fig = go.Figure()

    # Add a gauge chart to the figure
    fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = reservoir_level,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Reservoir Level"},
        gauge = {
            'axis': {'range': [0, maximum_reservoir_level]},
            'bar': {'color': "blue"},
            'steps' : [
                {'range': [0, critical_reservoir_level], 'color': "red"},
                {'range': [critical_reservoir_level, maximum_reservoir_level], 'color': "green"}
            ],
        }
    ))

    # Convert the figure to JSON
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graph1JSON, graph2JSON, plot_json
    
def plot_reservoir_level_charts(reservoir_name):
    
    reservoir = session.query(Reservoirs).filter(Reservoirs.reservoir_name == reservoir_name).first()

    if reservoir is None:
        abort(404) 
    
    reservoir_data = reservoir_data_to_dict_list(reservoir_id=reservoir.id)
    df = pd.DataFrame(reservoir_data)

    critical_reservoir_level = reservoir.critical_level

    level_fig = px.area(df, x='date', y='reservoir_level',
                        labels={'x': 'Date', 'y': 'Reservoir Level'},
                        title=f"{reservoir.reservoir_name} Reservoir Levels")
    level_fig.add_hline(y=critical_reservoir_level, line_dash="dot",
                        line_color="red", annotation_text="Critical Level")
    
    level_graphJSON = json.dumps(level_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    volume_fig = px.area(df, x='date', y='reservoir_volume',
                         labels={'x': 'Date', 'y': 'Reservoir Volume'},
                         title=f"{reservoir.reservoir_name} Reservoir Volumes")
    volume_graphJSON = json.dumps(volume_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return (level_graphJSON, volume_graphJSON)


def plot_dam_level_charts(dam_name):
    dam = session.query(Dams).filter(Dams.dam_name == dam_name).first()

    if dam is None:
        abort(404)

    dam_data = dams_data_to_dict_list(dam_id=dam.id)
    df = pd.DataFrame(dam_data)
    
    # Get the real value from the database when data is made available
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

    return (dam_graph1JSON, dam_graph2JSON, dam_graph3JSON)