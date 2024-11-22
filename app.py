from dash import Dash, html, dash_table, dcc, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import geopandas as gpd

# Load data
df = pd.read_csv("Data/df_improved.csv")
hospitals_and_clinics = pd.read_csv("Data/hospitals_and_clinics.csv")
total_cases_and_deaths_with_region = gpd.read_file("Data/total_cases_and_deaths_with_region/total_cases_and_deaths_with_region.shp")
total_cases_and_deaths_with_region['geometry'] = total_cases_and_deaths_with_region['geometry'].simplify(tolerance=0.01, preserve_topology=True)  # Simplify geometry for faster loading
total_cases_and_deaths_with_region.set_crs(epsg=4326, inplace=True)

# Define initial line graph
total_per_year = df.groupby('Date')[['Dengue_Cases', 'Dengue_Deaths']].sum().reset_index()
total_per_year_graph = px.line(
    total_per_year,
    x='Date',
    y=['Dengue_Cases', 'Dengue_Deaths'],
    labels={'value': 'Count', 'Date': 'Year'},
    title='Dengue Cases and Deaths Over Time',
    color_discrete_map={'Dengue_Cases': '#28AFB0', 'Dengue_Deaths': '#F4D35E'}  # Updated colors
)
total_per_year_graph.update_layout(
    paper_bgcolor='#1D2419',  # outside bg BLACK
    plot_bgcolor='#1D2419',  # inside bg BLACK
    font=dict(color='#FFFFFF'),  # font WHITE
    title=dict(font=dict(size=20, color='#FFFFFF')),  # Title 

    xaxis=dict( #x-axis properites
        tickformat="%Y",
        range=["2016-01-01", "2020-12-31"],
        dtick="M12",
        linecolor='#FFFFFF',  # Axis line color WHITE
        gridcolor='#19647E',  # Gridline color YELLOW
        zeroline=False,
        title=dict(text='Year', font=dict(color='#FFFFFF'))  # X-axis title font WHITE
    ),
    yaxis=dict(
        title=dict(text='Count', font=dict(color='#FFFFFF')),  # Y-axis title font WHITE
        linecolor='#FFFFFF',  # Axis line color font WHITE
        gridcolor='#19647E',  # Gridline color YELLOW
        zeroline=False,
    ),
    legend=dict(
        title=dict(text='Metric', font=dict(color='#FFFFFF')),  # title WHITE
        font=dict(color='#FFFFFF')  # font color WHITE
    ),
    hovermode='x unified'  
)
#--------------------ACTUAL APP-------------------------------------------------------------------------------
# External stylesheets
external_stylesheets = [
    dbc.themes.FLATLY, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css", #for the icons
]

app = Dash(__name__, external_stylesheets=external_stylesheets)

# App Layout
app.layout = html.Div(
    style={
        'backgroundColor': '#1D2419',  # layout bg BLACK
        'color': '#FFFFFF',           # font WHITE
        'padding': '20px',
    },
    children=[
        dbc.Container([
            # TITLE ROW
            dbc.Row(
                dbc.Col(
                    html.H1("Philippine Dengue Cases and Deaths (2016-2020)", 
                            className="text-center mt-4",
                            style={'color': '#FFFFFF'}  # White font color
                    )
                )
            ),

            # 4 INFO CARDS ROW
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4([
                                html.I(className="fas fa-viruses me-2"),
                                "Total Cases across all years:"
                            ], className="card-title", style={'color': '#FFFFFF'}),
                            html.H2(f"{df['Dengue_Cases'].sum():,}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#19647E",  # COLOR BLACK
                        inverse=True,
                        className="text-center shadow-sm",
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4([
                                html.I(className="fas fa-skull-crossbones me-2"),
                                "Total Deaths across all years:"
                            ], className="card-title", style={'color': '#FFFFFF'}),
                            html.H2(f"{df['Dengue_Deaths'].sum():,}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#EE964B",  # ORANGE
                        inverse=True,
                        className="text-center shadow-sm",
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4([
                                html.I(className="fas fa-chart-line me-2"),
                                "Average Cases per Year:"
                            ], className="card-title", style={'color': '#FFFFFF'}),
                            html.H2(f"{(df['Dengue_Cases'].sum() / 5):,.2f}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#28AFB0",  # BLUE
                        inverse=True,
                        className="text-center shadow-sm",
                    ),
                    width=3
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4([
                                html.I(className="fas fa-heartbeat me-2"),
                                "Average Deaths per Year:"
                            ], className="card-title", style={'color': '#FFFFFF'}),
                            html.H2(f"{(df['Dengue_Deaths'].sum() / 5):,.2f}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#F4D35E",  # YELLWO
                        inverse=True,
                        className="text-center shadow-sm",
                    ),
                    width=3
                ),
            ], className="mt-4 mb-2"),

            # Line Chart
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Total Dengue Cases and Deaths Over Time", style={'color': '#FFFFFF'})),
                        dbc.CardBody(dcc.Graph(figure=total_per_year_graph, id='total-cases-deaths-graph'))
                    ], style={'backgroundColor': '#19647E'}),
                    width=12
                )
            ], className="mt-4"),

            # Pie Chart and Choropleth Map
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Dengue Cases/Deaths per Island", style={'color': '#FFFFFF'})),
                        dbc.CardBody([
                            dcc.Graph(id='pie-graph'),
                            dcc.Store(id='metric-store', data='Cases')
                        ])
                    ], style={'backgroundColor': '#19647E'}),
                    width=6
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Dengue Cases/Deaths by Region", style={'color': '#FFFFFF'})),
                        dbc.CardBody(dcc.Graph(id='choropleth-with-hospitals'))
                    ], style={'backgroundColor': '#19647E'}),
                    width=6
                )
            ], className="mt-4"),

            # Buttons Row
            dbc.Row(
                dbc.Col(
                    dbc.ButtonGroup([
                        dbc.Button("Cases", color="warning", id='cases_button', n_clicks=0,
                                   style={'backgroundColor': '#28AFB0', 'borderColor': '#FFFFFF', 'color': '#FFFFFF'}),
                        dbc.Button("Deaths", color="danger", id='deaths_button', n_clicks=0,
                                   style={'backgroundColor': '#EE964B', 'borderColor': '#FFFFFF', 'color': '#FFFFFF'}),
                    ], size='lg'),
                    width=12,
                    className="d-flex justify-content-center mt-2"
                )
            ),

            # Bsr Bar Chart Section
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Cases and Deaths per Region and Year", style={'color': '#FFFFFF'})),
                        dbc.CardBody([
                            dcc.Checklist(
                                options=[{'label': region, 'value': region} for region in df["Region"].unique()],
                                id='stacked_region',
                                inline=True,
                                style={'backgroundColor': '#1D2419', 'color': '#FFFFFF'},  # White background with dark text
                                inputStyle={"margin-right": "10px"},  # space between boxes
                                #labelStyle={'color: '}
                            ),
                            dcc.Graph(id='region-graph'),
                            dcc.RangeSlider(
                                min=2016,
                                max=2020,
                                step=1,
                                count=1,
                                marks={i: {'label': str(i), 'style': {'color': '#FFFFFF'}} for i in range(2016, 2021)},
                                value=[2016, 2020],
                                id='stacked_slider'
                            )
                        ])
                    ], style={'backgroundColor': '#19647E'}),
                    width=12
                ),
                className="mt-4"
            ),

            # Specific Region Line Chart Section
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Cases and Deaths for Specific Region and Year", style={'color': '#FFFFFF'})),
                        dbc.CardBody([
                            dcc.Dropdown(
                                options=[{'label': region, 'value': region} for region in df["Region"].unique()],
                                multi=False,
                                placeholder="Choose which region to display",
                                id='specific_dropdown',
                                style={'backgroundColor': '#FFFFFF', 'color': '#1D2419'}
                            ),
                            dcc.Graph(id='specific-region-graph'),
                            dcc.RangeSlider(
                                min=2016,
                                max=2020,
                                step=1,
                                count=1,
                                marks={i: {'label': str(i), 'style': {'color': '#FFFFFF'}} for i in range(2016, 2021)},
                                value=[2016, 2020],
                                id='specific_slider'
                            )
                        ])
                    ], style={'backgroundColor': '#19647E'}),
                    width=12
                ),
                className="mt-4 mb-4"
            )
        ]#,fluid=True
        )
    ]
)


# --------------------------Callbacks-------------------------------------------------------------------------------------------------------------------------

# FOR PIE AND CHOROPLETH ROW
    #BuTTONS
@app.callback(
    Output('metric-store', 'data'),
    [Input('cases_button', 'n_clicks'),
     Input('deaths_button', 'n_clicks')],
    [State('metric-store', 'data')]
)
def update_metric(cases_n_clicks, deaths_n_clicks, current_metric):
    
    cases_n_clicks = cases_n_clicks or 0
    deaths_n_clicks = deaths_n_clicks or 0  #bad logic fix later

    if cases_n_clicks > deaths_n_clicks:
        return 'Cases'
    elif deaths_n_clicks > cases_n_clicks:
        return 'Deaths'
    else:
        return current_metric


    # Update pie chart based on button
@app.callback(
    Output('pie-graph', 'figure'),
    Input('metric-store', 'data')
)
def update_pie_chart(metric):
    values = 'Dengue_Cases' if metric == 'Cases' else 'Dengue_Deaths'
    title = f'Dengue {metric} per Island'
    colors = ['#28AFB0', '#F4D35E', '#EE964B', '#19647E']  # Custom color theme

    fig = px.pie(
        df,
        names='Island',
        values=values,
        hole=0.4,
        title=title,
        color_discrete_sequence=colors
    )
    fig.update_traces(textinfo='percent+label')

    fig.update_layout(
        paper_bgcolor='#1D2419',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        width=600,
        height=600,
    )
    return fig

    # Update choropleth map based on button
@app.callback(
    Output('choropleth-with-hospitals', 'figure'),
    Input('metric-store', 'data')
)
def update_choropleth(metric):
    metric_column = 'Dengue_Cas' if metric == 'Cases' else 'Dengue_Dea'
    
   
    color_scale = [
        [0.0, '#FFFFFF'],  [1.0, '#EE964B']   # WHITE TO ORANGE
    ]

    fig = px.choropleth_mapbox(
        total_cases_and_deaths_with_region,
        geojson=total_cases_and_deaths_with_region.__geo_interface__,
        locations=total_cases_and_deaths_with_region.index,
        color=metric_column,
        hover_name='Region',
        mapbox_style="carto-darkmatter",  # MAKE OWN MAPBOX STYLE LATER USE DARKMATTER FOR NOW
        zoom=4,
        center={"lat": 12.8797, "lon": 121.7740},
        opacity=0.7,
        color_continuous_scale=color_scale,  # Use the custom color scale
        title=f"Dengue {metric} by Region",
    )

    #for the hospital and lcinic points
    fig.add_scattermapbox(
        lat=hospitals_and_clinics['lat'],
        lon=hospitals_and_clinics['lon'],
        mode='markers',
        marker=dict(size=5, color='#19647E', opacity=0.7),
        text=hospitals_and_clinics['name'],
        hoverinfo = "text",
        
    
    )

    fig.update_layout(
        paper_bgcolor='#1D2419',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        legend=dict(font=dict(color='#FFFFFF')),
        width=600,
        height=600,
    )
    return fig


# Update stacked bar chart
@app.callback(
    Output("region-graph", 'figure'),
    [Input("stacked_region", 'value'),
     Input("stacked_slider", "value")]
)
def update_stacked_bar(regions, years):
    if regions is None or not regions:
        # Return styled empty bar chart when no regions are selected
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="No Region Selected",
                paper_bgcolor='#1D2419',
                plot_bgcolor='#1D2419',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    title="Region",
                    linecolor='#FFFFFF',
                    gridcolor='#19647E',
                    zeroline=False,
                ),
                yaxis=dict(
                    title="Count",
                    linecolor='#FFFFFF',
                    gridcolor='#19647E',
                    zeroline=False,
                ),
            )
        )

    # Filter the data based on selected regions and year range
    filtered_df = df[(df["Region"].isin(regions)) & (df["Year"].between(years[0], years[1]))]

    if filtered_df.empty:
        # Return styled empty bar chart when no data is available
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="No Data Available for Selected Regions and Years",
                paper_bgcolor='#1D2419',
                plot_bgcolor='#1D2419',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    title="Region",
                    linecolor='#FFFFFF',
                    gridcolor='#19647E',
                    zeroline=False,
                ),
                yaxis=dict(
                    title="Count",
                    linecolor='#FFFFFF',
                    gridcolor='#19647E',
                    zeroline=False,
                ),
            )
        )

    # Group the filtered data
    filtered_df = filtered_df.groupby(['Region', 'Year'], as_index=False).sum()

    # Create a stacked bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df['Region'],
        y=filtered_df['Dengue_Cases'] - filtered_df['Dengue_Deaths'],  # Non-death cases
        name='Dengue Cases (Excluding Deaths)',
        marker_color='#28AFB0'  # Teal
    ))

    fig.add_trace(go.Bar(
        x=filtered_df['Region'],
        y=filtered_df['Dengue_Deaths'],  # Deaths
        name='Dengue Deaths',
        marker_color='#F4D35E'  # Yellow
    ))

    # Update layout for stacked bar chart
    fig.update_layout(
        barmode='stack',  # Stacked bars
        title="Cases and Deaths per Region and Year",
        paper_bgcolor='#1D2419',
        plot_bgcolor='#1D2419',
        font=dict(color='#FFFFFF'),
        
        xaxis=dict(
            title=dict(text="Region", font=dict(color='#FFFFFF')),
            linecolor='#FFFFFF',
            gridcolor='#19647E'
        ),
        yaxis=dict(
            title=dict(text="Count", font=dict(color='#FFFFFF')),
            linecolor='#FFFFFF',
            gridcolor='#19647E'
        ),
        legend=dict(font=dict(color='#FFFFFF')),
        hovermode='x unified',
    )

    return fig


# Update specific region line chart
@app.callback(
    Output('specific-region-graph', 'figure'),
    [Input('specific_dropdown', 'value'),
     Input('specific_slider', 'value')]
)
def update_specific_region_graph(selected_region, selected_years):
    if not selected_region:
        return go.Figure(
            data=[], 
            layout=go.Layout(
                title="No Region Selected",
                paper_bgcolor='#1D2419',
                plot_bgcolor='#1D2419',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#19647E'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#19647E'),
            )
        )

    filtered_df = df[
        (df["Region"] == selected_region) & (df["Year"].between(selected_years[0], selected_years[1]))
    ]

    if filtered_df.empty:
        return go.Figure(
            data=[], 
            layout=go.Layout(
                title="No Data Available for Selected Region and Years",
                paper_bgcolor='#1D2419',
                plot_bgcolor='#1D2419',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#19647E'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#19647E'),
            )
        )

    aggregated_df = filtered_df.groupby(['Date'], as_index=False).sum()
    melted_df = aggregated_df.melt(
        id_vars=['Date'], value_vars=['Dengue_Cases', 'Dengue_Deaths'], var_name='Metric', value_name='Count'
    )

    fig = px.line(
        melted_df,
        x='Date',
        y='Count',
        color='Metric',
        title=f'Dengue Cases and Deaths Over Time in {selected_region}',
        color_discrete_map={'Dengue_Cases': '#28AFB0', 'Dengue_Deaths': '#F4D35E'}
    )

    fig.update_layout(
        paper_bgcolor='#1D2419',
        plot_bgcolor='#1D2419',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        xaxis=dict(title=dict(text="Date", font=dict(color='#FFFFFF')), linecolor='#FFFFFF', gridcolor='#19647E'),
        yaxis=dict(title=dict(text="Number of Cases/Deaths", font=dict(color='#FFFFFF')), linecolor='#FFFFFF', gridcolor='#19647E'),
        legend=dict(font=dict(color='#FFFFFF')),
        hovermode='x unified',
    )
    return fig

# ------------------------------------------run app ------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
