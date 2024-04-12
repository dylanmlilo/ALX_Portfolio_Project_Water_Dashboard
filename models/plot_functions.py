from flask import abort
import pandas as pd
import json
import plotly
import plotly_express as px
import plotly.graph_objects as go
from models.engine.database import session, dams_data_to_dict_list, reservoir_data_to_dict_list, current_reservoir_levels, current_dam_percentages
from models.dams import Dams, DamData
from models.reservoirs import Reservoirs, ReservoirData
from datetime import datetime, timedelta



def today_date():
    today_date = datetime.today()

    formatted_date = today_date.strftime('%a, %d %B %Y')
    
    return formatted_date

def plot_home_page_charts():
    dam_data = dams_data_to_dict_list()
    df = pd.DataFrame(dam_data)
    fig1 = px.area(df, x = 'date', y = 'dam_percentage', color='dam_name',
                   labels={'x' : 'Date', 'y' : ' Dam Percentage'},
                   title = "Dam Percentages")
    fig1.update_traces(mode='lines+markers', marker_size=8, stackgroup='', line_shape='spline')
    fig1.update_layout(
    legend_title_text='Dams',
    title={
        'text': "Dam Percentages Levels",
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Dam Percentage (%)",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    
    reservoir_data = reservoir_data_to_dict_list()
    df = pd.DataFrame(reservoir_data)
    fig2 = px.area(df, x = 'date', y = 'reservoir_level', color='reservoir_name',
                   labels={'x' : 'Date', 'y' : 'Reservoir Level'},
                   title = "Reservoir Levels")
    fig2.update_traces(mode='lines+markers', marker_size=8, stackgroup='',line_shape='spline') #, stackgroup='one' or None
    fig2.update_layout(
    legend_title_text='Reservoirs',
    title={
        'text': "Reservoir Levels",
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Reservoir Level (ft), Crit clear and raw (m)",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    try:
        reservoir_names = session.query(Reservoirs.reservoir_name).all()
    except:
        session.rollback()
    finally:
        session.close()
    reservoir_names = [name[0] for name in reservoir_names]
    
    gauge_reservoir_figures = []
    for reservoir_name in reservoir_names:
        try:
            reservoir = session.query(Reservoirs).filter(Reservoirs.reservoir_name == reservoir_name).first()
        except:
            session.rollback()
        finally:
            session.close()
        try:
            current_level = current_reservoir_levels(reservoir_name)
            maximum_level = reservoir.max_level
            critical_level = reservoir.critical_level

            fig = go.Figure()
            
            num_ticks = 7

            tickvals = [round(i * (maximum_level / (num_ticks - 1)), 2) for i in range(num_ticks)]
            ticktext = [str(val) for val in tickvals]
            
            if current_level > critical_level:
                number_color = {'font': {'color': 'rgb(9, 9, 54)'}}
            else:
                number_color = {'font': {'color': 'red'}}

            fig.add_trace(go.Indicator(
                mode = "gauge+number",
                number = number_color,
                value = current_level,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{reservoir_name} Reservoir Level", 'font': {'color': 'rgb(9, 9, 54)'}},
                gauge = {
                    'axis': {
                            'range': [0, maximum_level],
                            'tickvals': tickvals,
                            'ticktext': ticktext,
                            'tickfont': {'size': 13, 'color':'rgb(9, 9, 54)'},
                        },
                    'bar': {'color': "rgba(50, 50, 255, 0.9)"},
                    'steps' : [
                        {'range': [0, critical_level], 'color': "rgba(255, 0, 0, 0.850)"},
                        {'range': [critical_level, maximum_level], 'color': "rgba(47, 182, 182, 0.767)"}
                    ],
                }
            ))
            
            fig.update_layout(margin=dict(t=0, b=0, l=40, r=50))
            fig.update_layout(height=450, width=400)
            fig.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)')
            gauge_reservoir_figures.append(fig)

        except Exception as e:
            print(f"Error fetching data for {reservoir_name}: {e}")
        
    gauge_reservoir_json = [json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) for fig in gauge_reservoir_figures]
    
    
    
    try:
        dam_names = session.query(Dams.dam_name).all()
    except:
        session.rollback()
    finally:
        session.close()
    dam_names = [name[0] for name in dam_names]
    
    gauge_dam_figures = []
    for dam_name in dam_names:
        dam = session.query(Dams).filter(Dams.dam_name == dam_name).first()
        try:
            current_level = current_dam_percentages(dam_name)
            maximum_level = 100
            critical_level = 40

            fig = go.Figure()
            
            num_ticks = 7

            tickvals = [round(i * (maximum_level / (num_ticks - 1)), 2) for i in range(num_ticks)]
            ticktext = [str(val) for val in tickvals]

            if current_level > critical_level:
                number_color = {'font': {'color': 'rgb(9, 9, 54)'}}
            else:
                number_color = {'font': {'color': 'red'}}

            fig.add_trace(go.Indicator(
                mode = "gauge+number",
                number = number_color,
                value = current_level,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{dam_name} Percentage", 'font': {'color': 'rgb(9, 9, 54)'}},
                gauge = {
                    'axis': {
                            'range': [0, maximum_level],
                            'tickvals': tickvals,
                            'ticktext': ticktext,
                            'tickfont': {'size': 13, 'color':'rgb(9, 9, 54)'},
                        },
                    'bar': {'color': "rgba(50, 50, 255, 0.9)"},
                    'steps' : [
                        {'range': [0, critical_level], 'color': "rgba(255, 0, 0, 0.850)"},
                        {'range': [critical_level, maximum_level], 'color': "rgba(47, 182, 182, 0.767)"}
                    ],
                }
            ))
            fig.update_layout(margin=dict(t=0, b=0, l=40, r=50))
            fig.update_layout(height=450, width=400)
            fig.update_layout(paper_bgcolor='rgba(0, 0, 0, 0)')
            gauge_dam_figures.append(fig)

        except Exception as e:
            print(f"Error fetching data for {dam_name}: {e}")
        
    gauge_dam_json = [json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) for fig in gauge_dam_figures] 
    
    return graph1JSON, graph2JSON, gauge_reservoir_json, gauge_dam_json
    
def plot_reservoir_level_charts(reservoir_name):
    try:
        reservoir = session.query(Reservoirs).filter(Reservoirs.reservoir_name == reservoir_name).first()
    except:
        session.rollback()
    finally:
        session.close()
        
    if reservoir is None:
        abort(404) 
    
    reservoir_data = reservoir_data_to_dict_list(reservoir_id=reservoir.id)
    df = pd.DataFrame(reservoir_data)

    critical_reservoir_level = reservoir.critical_level

    level_fig = px.area(df, x='date', y='reservoir_level',
                        labels={'x': 'Date', 'y': 'Reservoir Level'},
                        title=f"{reservoir.reservoir_name} Reservoir Levels")
    level_fig.add_hline(y=critical_reservoir_level, line_dash="solid",
                        line_color="red", annotation_text="Critical Reservoir Level")
    level_fig.update_traces(mode='lines+markers', marker_size=8, line_shape='spline')
    level_fig.update_layout(
    title={
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Reservoir Level",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    
    level_graphJSON = json.dumps(level_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    volume_fig = px.area(df, x='date', y='reservoir_volume',
                         labels={'x': 'Date', 'y': 'Reservoir Volume'},
                         title=f"{reservoir.reservoir_name} Reservoir Volumes")
    volume_fig.update_traces(mode='lines+markers', marker_size=8, line_shape='spline')
    volume_fig.update_layout(
    title={
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Reservoir Volume",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    volume_graphJSON = json.dumps(volume_fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return (level_graphJSON, volume_graphJSON)


def plot_dam_level_charts(dam_name):
    try:
        dam = session.query(Dams).filter(Dams.dam_name == dam_name).first()
    except:
        session.rollback()
    finally:
        session.close()
        
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
    dam_fig1.add_hline(y=critical_dam_percentage, line_dash="solid",
                   line_color="red", annotation_text="Critical Dam Percentage")
    dam_fig1.update_traces(mode='lines+markers', marker_size=8, line_shape='spline')
    dam_fig1.update_layout(
    title={
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Dam Percentage (%)",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    dam_graph1JSON = json.dumps(dam_fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    dam_fig2 = px.area(df, x = 'date', y = 'dam_reading',
                       labels={'x' : 'Date', 'y' : ' Dam Reading'},
                       title = f"{dam.dam_name} Readings")
    dam_fig2.update_traces(mode='lines+markers', marker_size=8, line_shape='spline')
    # y_min = float(df['dam_reading'].min())
    # y_max = float(df['dam_volume'].max())
    # y_range = [y_min, y_max * 1.5]
    # dam_fig2.update_yaxes(range=y_range)
    dam_fig2.update_layout(
    title={
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Dam Reading",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    dam_graph2JSON = json.dumps(dam_fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    dam_fig3 = px.area(df, x = 'date', y = 'dam_volume',
                       labels={'x' : 'Date', 'y' : ' Dam Volume'}, 
                       title = f"{dam.dam_name} Volumes")
    dam_fig3.update_traces(mode='lines+markers', marker_size=8, line_shape='spline')
    dam_fig3.update_layout(
    title={
        'x': 0.5,
        'y': 0.9,
        'font': {
            'size': 30,
            'family': 'Arial'
        }
    },
    xaxis_title_text="Date",
    yaxis_title_text="Dam Volumes",
    xaxis_title_font_size=20,
    yaxis_title_font_size=18,
    legend_title_font={'size': 18}
)
    dam_graph3JSON = json.dumps(dam_fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return (dam_graph1JSON, dam_graph2JSON, dam_graph3JSON)