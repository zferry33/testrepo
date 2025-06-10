# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique().tolist()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: RangeSlider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(i): str(int(i)) for i in range(0, int(max_payload) + 1, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: Callback for pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df

    if entered_site == 'ALL':
        # Filter only successful launches
        filtered_df = spacex_df[spacex_df['class'] == 1]
        
        # Group by Launch Site and count successes
        data = filtered_df['Launch Site'].value_counts().reset_index()
        data.columns = ['pie chart names', 'class']

        fig = px.pie(data, 
                     values='class', 
                     names='pie chart names', 
                     title='Total Success Launches By Site')
        return fig
    else:
        # Filter dataframe for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Group by class (success=1, failure=0) and count
        data = filtered_df['class'].value_counts().reset_index()
        data.columns = ['pie chart names', 'class']

        fig = px.pie(data, 
                     values='class', 
                     names='pie chart names', 
                     title=f'Total Success vs. Failure for site {entered_site}')
        return fig

# TASK 4: Callback for scatter chart
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
