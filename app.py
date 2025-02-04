import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
import logging

# Set up production-grade logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define the path to the CSV file.
csv_file = os.path.join(os.getcwd(), 'data', 'data.csv')

# Try to load the CSV file. If it exists, generate the line graph.
if os.path.exists(csv_file):
    try:
        df = pd.read_csv(csv_file)
        # Use the first two columns as x and y (adjust if needed).
        x_col = df.columns[0]
        y_col = df.columns[1]
        logging.info("Generating line graph for %s vs %s", y_col, x_col)
        
        # Create a line graph with markers and text labels showing y values.
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=f'Line Graph of {y_col} vs {x_col}'
        )
        fig.update_traces(
            mode='lines+markers+text',
            text=df[y_col].astype(str),
            textposition='top center',
            marker=dict(size=8)
        )
    except Exception as e:
        logging.error("Error processing CSV file: %s", e)
        fig = px.scatter(title='Error processing CSV file')
else:
    logging.error("CSV file not found at: %s", csv_file)
    fig = px.scatter(title='No Data Available')

# Initialize Dash app.
app = dash.Dash(__name__)
server = app.server  # Expose the Flask server (for production deployment if needed).

# Define the layout for the Dash app.
app.layout = html.Div([
    html.Div([
        html.Img(src="/pictures/teslalogo.jpg", style={'height': '60px'}),
        html.H1("CSV Line Graph with Dash", style={'display': 'inline-block', 'marginLeft': '20px'})
    ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px'}),
    dcc.Graph(
        id='line-graph',
        figure=fig
    )
])


# Run the app.
if __name__ == '__main__':
    # In production, consider using a WSGI server like Gunicorn.
    app.run_server(debug=False, host='0.0.0.0', port=5000)
