import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Search for the specific CSV files in the exported_data folder.
exported_dir = os.path.join(os.getcwd(), "exported_data")
cell_file = None
face_file = None
for filename in os.listdir(exported_dir):
    if "cells__SV_T__1" in filename and filename.endswith(".csv"):
        cell_file = os.path.join(exported_dir, filename)
    if "faces__SV_T__1" in filename and filename.endswith(".csv"):
        face_file = os.path.join(exported_dir, filename)

if not cell_file:
    logging.error("Cell SV_T file not found.")
if not face_file:
    logging.error("Face SV_T file not found.")

# Load CSV files.
df_cell = pd.read_csv(cell_file) if cell_file else pd.DataFrame()
df_face = pd.read_csv(face_file) if face_file else pd.DataFrame()

# Create a column for row number.
if not df_cell.empty:
    df_cell["Index"] = df_cell.index + 1
    fig_cell = px.scatter(df_cell, x="Index", y="Value", title="Temperature (cell)")
else:
    fig_cell = px.scatter(title="No cell data available")

if not df_face.empty:
    df_face["Index"] = df_face.index + 1
    fig_face = px.scatter(df_face, x="Index", y="Value", title="Temperature (face)")
else:
    fig_face = px.scatter(title="No face data available")

# Calculate the highest cell temperature and convert to Celsius.
if not df_cell.empty:
    max_temp_kelvin = df_cell["Value"].max()
    max_temp_celsius = max_temp_kelvin - 273.15
    highest_temp_text = f"Highest temperature (cell): {max_temp_kelvin:.2f} K ({max_temp_celsius:.2f} °C)"
else:
    highest_temp_text = "No cell data available."

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.Img(src="/pictures/teslalogo.jpg", style={'height': '60px'}),
        html.H1("Simulation Temperature Data", style={'display': 'inline-block', 'marginLeft': '20px'})
    ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px'}),
    html.Div(highest_temp_text, style={'textAlign': 'center', 'fontSize': '24px', 'margin': '20px'}),
    dcc.Graph(id="cell-graph", figure=fig_cell),
    dcc.Graph(id="face-graph", figure=fig_face)
])

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=5000)
