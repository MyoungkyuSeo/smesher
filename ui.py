import os
import base64
import time
import logging
import dash
from dash import dcc, html, Output, Input, State
import pandas as pd
import plotly.express as px
from preprocess import main as preprocess_main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_graphs():
    exported_dir = os.path.join(os.getcwd(), "exported_data")
    cell_file = None
    face_file = None
    for filename in os.listdir(exported_dir):
        if "cells__SV_T__1" in filename and filename.endswith(".csv"):
            cell_file = os.path.join(exported_dir, filename)
        if "faces__SV_T__1" in filename and filename.endswith(".csv"):
            face_file = os.path.join(exported_dir, filename)
    if cell_file:
        df_cell = pd.read_csv(cell_file)
        df_cell["Index"] = df_cell.index + 1
        fig_cell = px.scatter(df_cell, x="Index", y="Value", title="Temperature (cell)",
                              labels={'Index': 'Mesh #', 'Value': 'Kelvins'})
        max_temp = df_cell["Value"].max()
        max_temp_text = f"Highest temperature (cell): {max_temp:.2f} K ({max_temp - 273.15:.2f} °C)"
    else:
        fig_cell = px.scatter(title="No cell data available")
        max_temp_text = "No cell data available."
    if face_file:
        df_face = pd.read_csv(face_file)
        df_face["Index"] = df_face.index + 1
        fig_face = px.scatter(df_face, x="Index", y="Value", title="Temperature (face)",
                              labels={'Index': 'Mesh #', 'Value': 'Kelvins'})
    else:
        fig_face = px.scatter(title="No face data available")
    return fig_cell, fig_face, max_temp_text

app = dash.Dash(__name__)
server = app.server

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Orbitron', sans-serif;
            }
            .futuristic-header {
                color: #00e6ff;
                text-shadow: 0 0 10px #00e6ff;
            }
            .futuristic-text {
                font-size: 20px;
                color: #cfcfcf;
            }
            .futuristic-button {
                background-color: #00e6ff;
                border: none;
                color: #121212;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                box-shadow: 0 0 10px #00e6ff;
            }
            .futuristic-button:hover {
                background-color: #00c2cc;
            }
            .upload-box {
                border: 2px dashed #00e6ff;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
                color: #00e6ff;
            }
            .max-temp {
                font-size: 28px;
                color: #ff007f;
                font-weight: bold;
                text-shadow: 0 0 10px #ff007f;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div([
    # Header: Logo above title.
    html.Div([
        html.Img(src="/assets/teslalogo.png", style={'height': '80px', 'marginBottom': '10px'}),
        html.H1("Max Temperature Solver", className="futuristic-header")
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.Div("Upload all of your .h5 Ansys Fluent solution file here",
             className="futuristic-text", style={'textAlign': 'center', 'marginBottom': '10px'}),
    
    dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag and Drop or ", html.A("Select Solution File")]),
        style={"width": "90%", "height": "60px", "lineHeight": "60px", "margin": "0 auto", "marginBottom": "10px"},
        className="upload-box",
        multiple=False
    ),
    html.Div(id="uploaded-file", style={"textAlign": "center", "margin": "10px", "fontWeight": "bold"}),
    
    html.Div(id="load-button-container"),
    
    html.Div(id="status-message", style={"textAlign": "center", "margin": "10px"}),
    
    # Highest temperature display above graphs.
    html.Div(id="max-temp", className="max-temp", style={"textAlign": "center"}),
    
    html.Div(
        dcc.Graph(id="cell-graph"),
        style={'margin': '20px auto', 'width': '90%'}
    ),
    html.Div(
        dcc.Graph(id="face-graph"),
        style={'margin': '20px auto', 'width': '90%'}
    )
])

@app.callback(
    Output("uploaded-file", "children"),
    Input("upload-data", "filename")
)
def display_uploaded_filename(filename):
    if filename:
        if ".dat.h5" not in filename:
            return "Did you put EVERY Ansys Solution file? (hint try .dat.h5)"
        return f"Uploaded file: {filename}"
    return "No file uploaded."

@app.callback(
    Output("load-button-container", "children"),
    Input("upload-data", "filename")
)
def update_load_button(filename):
    if filename and ".dat.h5" in filename:
        return html.Div([
            html.Button("Load Graph", id="preprocess-button", n_clicks=0, className="futuristic-button", style={"marginRight": "20px"}),
            dcc.Loading(
                id="loading-spinner",
                type="circle",
                children=html.Div(id="spinner-placeholder"),
                style={"display": "inline-block", "verticalAlign": "middle"}
            )
        ], style={"textAlign": "center", "margin": "20px"})
    return ""

@app.callback(
    Output("status-message", "children"),
    Output("cell-graph", "figure"),
    Output("face-graph", "figure"),
    Output("max-temp", "children"),
    Input("preprocess-button", "n_clicks"),
    State("upload-data", "contents"),
    State("upload-data", "filename")
)
def preprocess_and_update(n_clicks, contents, filename):
    if n_clicks < 1:
        if contents:
            return "File uploaded and waiting to load graph...", dash.no_update, dash.no_update, dash.no_update
        else:
            return "Awaiting file upload and preprocessing...", dash.no_update, dash.no_update, dash.no_update

    status = "Graph loading... "
    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_path = os.path.join(os.getcwd(), "data", filename)
            with open(file_path, "wb") as f:
                f.write(decoded)
            status += f"Uploaded file: {filename}. "
        except Exception as e:
            status += f"File upload failed: {str(e)}. "
            return status, dash.no_update, dash.no_update, dash.no_update
    else:
        status += "No file uploaded; using existing file in ./data. "
    
    time.sleep(3)
    try:
        preprocess_main()
        status += "Preprocessing complete. "
    except Exception as e:
        status += f"Preprocessing failed: {str(e)}"
        return status, dash.no_update, dash.no_update, dash.no_update
    
    fig_cell, fig_face, max_temp_text = load_graphs()
    return status, fig_cell, fig_face, max_temp_text

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=5000)
