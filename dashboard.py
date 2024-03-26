from flask import Flask, render_template, Input, Output
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Load your data (replace with your data loading logic)
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

@app.route('/dash')  # Define a route for the Dash app
def render_dash_app():
    return render_template('graph.html')

@app.callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
