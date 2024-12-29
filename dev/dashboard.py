import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import datetime as dt
# Load and preprocess data
data_file = "../data/power_usage.csv"
def load_data():
    df = pd.read_csv(data_file, parse_dates=['DateTime'])
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.sort_values(by='DateTime')
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['Day'] = df['DateTime'].dt.day
    df['Hour'] = df['DateTime'].dt.hour
    df['Minute'] = df['DateTime'].dt.minute

    # Calculate time intervals in seconds and energy (kWh)
    df['delta_t'] = df['DateTime'].diff().dt.total_seconds().fillna(0)

    # Cap delta_t to a reasonable maximum (e.g., 10 seconds)
    MAX_DELTA_T = 10  # Adjust this value based on expected measurement frequency
    df['delta_t'] = df['delta_t'].apply(lambda x: min(x, MAX_DELTA_T))

    # Calculate energy (kWh)
    df['Energy(kWh)'] = (df['Power(kW)'] * df['delta_t']) / 3600
    return df

def try_load_data():
    try:
        return load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['DateTime', 'Year', 'Month', 'Day', 'Hour', 'Power(kW)', 'Energy(kWh)'])

data = try_load_data()
currentYear = dt.date.today().year
valid_years = sorted(data['Year'].unique())
currentYear = currentYear if currentYear in valid_years else (valid_years[-1] if valid_years else None)

# German month names
MONTH_NAMES = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

# Power tariffs
TARIFFS = {
    "base_price": 8.00,  # CHF/month
    "energy_price": 13.40 / 100,  # CHF per kWh (converted from Rp./kWh)
    "system_services": 0.55 / 100,  # CHF per kWh
    "reserve_services": 0.23 / 100,  # CHF per kWh
}

# Initialize Dash app
app = dash.Dash(__name__, external_scripts=['https://cdn.plot.ly/plotly-latest.min.js'])
app.title = "Power Usage Dashboard"

# Layout
# Layout Design
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f4f4f4",
        "padding": "10px",
        "minHeight": "100vh"
    },
    children=[
        # Header
        html.Div(
            style={
                "backgroundColor": "#2C3E50",
                "color": "#ECF0F1",
                "padding": "20px",
                "textAlign": "center",
                "borderRadius": "8px",
                "marginBottom": "20px"
            },
            children=[
                html.H1("Power Usage Dashboard", style={"margin": "0px", "fontWeight": "bold"}),
                html.P("Visualize your power usage data with interactive charts and detailed summaries."),
            ]
        ),

        # Content Wrapper
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "row",
                "gap": "20px",
                "margin": "0 auto",
                "maxWidth": "1200px"
            },
            children=[
                # Sidebar
                html.Div(
                    style={
                        "width": "25%",
                        "backgroundColor": "#ECF0F1",
                        "padding": "20px",
                        "borderRadius": "8px",
                        "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)"
                    },
                    children=[
                        html.H3("Controls", style={"marginBottom": "10px", "textAlign": "center"}),
                        dcc.Dropdown(
                            id='year-selector',
                            options=[{'label': str(year), 'value': year} for year in valid_years],
                            value=currentYear,
                            style={"marginBottom": "20px", "borderRadius": "4px"}
                        ),
                        html.Button(
                            "Refresh Data",
                            id='refresh-data-button',
                            style={
                                "width": "100%",
                                "padding": "10px",
                                "backgroundColor": "#2980B9",
                                "color": "#fff",
                                "border": "none",
                                "borderRadius": "4px",
                                "cursor": "pointer"
                            }
                        ),
                        html.Div(id='live-values', style={"marginTop": "20px", "textAlign": "center"}),
                        html.Div(id='cost-summary', style={"marginTop": "20px", "textAlign": "center"})
                    ]
                ),

                # Main Content
                html.Div(
                    style={
                        "flex": "1",
                        "backgroundColor": "#fff",
                        "padding": "20px",
                        "borderRadius": "8px",
                        "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)"
                    },
                    children=[
                        dcc.Graph(id='yearly-overview', style={"marginBottom": "20px"}),
                        dcc.Graph(id='monthly-detail', style={'display': 'none'}),
                        dcc.Graph(id='daily-detail', style={'display': 'none'}),
                        dcc.Graph(id='hourly-detail', style={'display': 'none'}),
                    ]
                )
            ]
        )
    ]
)


# Callbacks for interactivity
@app.callback(
    Output('yearly-overview', 'figure'),
    Input('year-selector', 'value')
)
def update_yearly_overview(selected_year):
    if selected_year is None or data.empty:
        return px.bar(title="Please select a year to view power usage.")

    yearly_data = data[data['Year'] == selected_year]
    if yearly_data.empty:
        return px.bar(title=f"No data available for {selected_year}.")
    monthly_summary = yearly_data.groupby('Month').agg({
        'Energy(kWh)': 'sum'
    }).reindex(range(1, 13), fill_value=0).reset_index()
    monthly_summary['Formatted Energy'] = monthly_summary['Energy(kWh)'].apply(lambda x: f"{x:.4f}")
    fig = px.bar(
        monthly_summary, 
        x='Month', 
        y='Energy(kWh)', 
        title=f"Total Monthly Power Usage for {selected_year} (kWh)",
        labels={"Energy(kWh)": "Total Energy (kWh)", "Month": "Month"},
        text="Formatted Energy"
    )
    fig.update_traces(customdata=monthly_summary['Month'], hoverinfo="x+y")
    fig.update_xaxes(
        ticktext=MONTH_NAMES, 
        tickvals=list(range(1, 13)),
    )
    return fig

@app.callback(
    [Output('monthly-detail', 'figure'), Output('monthly-detail', 'style'), Output('cost-summary', 'children')],
    [Input('yearly-overview', 'clickData'), Input('year-selector', 'value')]
)
def update_monthly_detail(clickData, selected_year):
    if clickData is None or selected_year is None:
        return {}, {'display': 'none'},  html.Div([
            html.H4("Monthly Cost Summary", style={"marginBottom": "10px"}),
            html.P("No data available, select a month")])

    selected_month = clickData['points'][0]['customdata']

    monthly_data = data[(data['Year'] == selected_year) & (data['Month'] == selected_month)]
    # Cost calculation for the month
    total_energy = monthly_data['Energy(kWh)'].sum()
    total_cost = (total_energy * (TARIFFS['energy_price'] + TARIFFS['system_services'] + TARIFFS['reserve_services']))
    total_cost += TARIFFS['base_price']  # Add monthly base price

    cost_summary = html.Div([
        html.H4("Monthly Cost Summary", style={"marginBottom": "10px"}),
        html.P(f"Total Energy Used: {total_energy:.2f} kWh"),
        html.P(f"Estimated Total Cost: CHF {total_cost:.2f}")
    ])

    daily_summary = monthly_data.groupby('Day').agg({
        'Energy(kWh)': 'sum'
    }).reindex(range(1, 32), fill_value=0).reset_index()
    daily_summary['Formatted Energy'] = daily_summary['Energy(kWh)'].apply(lambda x: f"{x:.4f}")
    fig = px.bar(
        daily_summary, 
        x='Day', 
        y='Energy(kWh)', 
        title=f"Total Daily Power Usage for {selected_year}-{MONTH_NAMES[selected_month-1]} (kWh)",
        labels={"Energy(kWh)": "Total Energy (kWh)", "Day": "Day"},
        text="Formatted Energy"
    )
    fig.update_traces(customdata=daily_summary['Day'], hoverinfo="x+y")
    fig.update_xaxes(range=[0.5, 31.5],dtick=1)
    return fig, {'display': 'block'}, cost_summary

@app.callback(
    [Output('daily-detail', 'figure'), Output('daily-detail', 'style')],
    [Input('monthly-detail', 'clickData'), Input('year-selector', 'value'), Input('yearly-overview', 'clickData')]
)
def update_daily_detail(clickData, selected_year, yearly_clickData):
    if clickData is None or selected_year is None or yearly_clickData is None:
        return {}, {'display': 'none'}

    selected_day = clickData['points'][0]['customdata']
    selected_month = yearly_clickData['points'][0]['customdata']

    daily_data = data[(data['Year'] == selected_year) & (data['Month'] == selected_month) & (data['Day'] == selected_day)]

    hourly_summary = daily_data.groupby('Hour').agg({
        'Energy(kWh)': 'sum'
    }).reindex(range(0, 24), fill_value=0).reset_index()
    hourly_summary['Formatted Energy'] = hourly_summary['Energy(kWh)'].apply(lambda x: f"{x:.4f}")

    fig = px.bar(
        hourly_summary, 
        x='Hour', 
        y='Energy(kWh)', 
        title=f"Total Hourly Power Usage for {selected_year}-{MONTH_NAMES[selected_month-1]}-{selected_day:02d}",
        labels={"Energy(kWh)": "Energy (kWh)", "Hour": "Hour"},
        text="Formatted Energy"
    )
    fig.update_traces(customdata=hourly_summary['Hour'], hoverinfo="x+y")
    fig.update_xaxes(range=[-0.5, 23.5],dtick=1)
    return fig, {'display': 'block'}

@app.callback(
    [Output('hourly-detail', 'figure'), Output('hourly-detail', 'style')],
    [Input('daily-detail', 'clickData'), Input('year-selector', 'value'), Input('yearly-overview', 'clickData'), Input('monthly-detail', 'clickData')]
)
def update_hourly_detail(clickData, selected_year, yearly_clickData, monthly_clickData):
    if clickData is None or selected_year is None or yearly_clickData is None:
        return {}, {'display': 'none'}

    selected_hour = clickData['points'][0]['customdata']
    selected_day = monthly_clickData['points'][0]['customdata']
    selected_month = yearly_clickData['points'][0]['customdata']
    hourly_data = data[(data['Year'] == selected_year) & (data['Month'] == selected_month) & (data['Day'] == selected_day) & (data['Hour'] == selected_hour)]
    minute_summary = hourly_data.groupby('Minute').agg({
        'Power(kW)': 'mean'
    }).reindex(range(0, 60), fill_value=0).reset_index()
    minute_summary['Formatted Energy'] = minute_summary['Power(kW)'].apply(lambda x: f"{x:.3f}")
    fig = px.bar(
        minute_summary,
        x='Minute',  # Minutes
        y='Power(kW)',
        title=f"Power Usage for {selected_year}-{MONTH_NAMES[selected_month-1]}-{selected_day:02d} {selected_hour:02d}:00",
        labels={"Power(kW)": "Power(kW)", "Minute": "Minute"},
        text="Formatted Energy"
    )
    
    # Set x-axis range and ticks
    fig.update_xaxes(
        range=[-0.5, 59.5],  # Ensure full minute range is shown
        tickvals=list(range(0, 60)),  # Force minute ticks
        ticktext=[f"{selected_hour:02d}:{minute:02d}" for minute in range(0, 60)],  # Format as %H:%M
    )
    return fig, {'display': 'block'}


@app.callback(
    [Output('year-selector', 'options'), Output('year-selector', 'value')],
    Input('refresh-data-button', 'n_clicks')
)
def refresh_data(n_clicks):
    global data
    data = try_load_data()
    options = [{'label': str(year), 'value': year} for year in sorted(data['Year'].unique())]
    default_year = dt.date.today().year if dt.date.today().year in data['Year'].unique() else None
    return options, default_year


@app.callback(
    Output('live-values', 'children'),
    Input('refresh-data-button', 'n_clicks')
)
def update_live_values(n_clicks):
    try:
        latest_row = pd.read_csv(data_file).iloc[-1]
        power = latest_row['Power(kW)']
        peak_current = latest_row.get('RMS_Current(A)', 'N/A')
        return [
            html.Div(f"Live Power Consumption: {power:.3f} kW", style={"marginTop": "10px"}),
            html.Div(f"Live Current Consumption: {peak_current:.3f} A", style={"marginTop": "10px"})
        ]
    except Exception as e:
        return html.Div(f"Error fetching live data: {e}", style={"marginTop": "10px", "color": "red"})

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)