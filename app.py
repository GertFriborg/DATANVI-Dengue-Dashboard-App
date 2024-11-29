from dash import Dash, html, dash_table, dcc, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import geopandas as gpd
from plotly.subplots import make_subplots

# Load data
df = pd.read_csv("Data/df_improved.csv")
hospitals_and_clinics = pd.read_csv("Data/hospitals_and_clinics.csv")
hospitals_per_island = pd.read_csv("Data/hospitals_per_island.csv")
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
    #title='Dengue Cases and Deaths Over Time',
    color_discrete_map={'Dengue_Cases': '#C7E5FF', 'Dengue_Deaths': '#EC7777'}  # Updated colors
)
total_per_year_graph.update_layout(
    paper_bgcolor='#393D3F',  # outside bg BLACK
    plot_bgcolor='#393D3F',  # inside bg BLACK
    font=dict(color='#FFFFFF'),  # font WHITE
    #title=dict(font=dict(size=20, color='#FFFFFF')),  # Title 

    xaxis=dict( #x-axis properites
        tickformat="%Y",
        range=["2016-01-01", "2020-12-31"],
        dtick="M12",
        linecolor='#FFFFFF',  # Axis line color WHITE
        gridcolor='#60B3F7',  # Gridline color YELLOW
        zeroline=False,
        title=dict(text='Year', font=dict(color='#FFFFFF'))  # X-axis title font WHITE
    ),
    yaxis=dict(
        title=dict(text='Count', font=dict(color='#FFFFFF')),  # Y-axis title font WHITE
        linecolor='#FFFFFF',  # Axis line color font WHITE
        gridcolor='#60B3F7',  # Gridline color YELLOW
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
        'backgroundColor': '#393D3F',  # layout bg BLACK
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
                        color="#60B3F7",  # COLOR BLACK
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
                        color="#EC7777",  # ORANGE
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
                            html.H2(f"{(df['Dengue_Cases'].sum() / 5):,.0f}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#60B3F7",  # BLUE
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
                            html.H2(f"{(df['Dengue_Deaths'].sum() / 5):,.0f}", 
                                    className="card-text", style={'color': '#FFFFFF'}),
                        ]),
                        color="#EC7777",  # YELLWO
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
                    ], style={'backgroundColor': '#60B3F7'}),
                    width=12
                )
            ], className="mt-4"),

            # Pie Chart and Choropleth Map
            dbc.Row([
                dbc.Col(
                    [   
                        dbc.Card([
                            dbc.CardHeader(html.H4("Number of Hospitals per Island Group", style={'color': '#FFFFFF'})),
                            dbc.CardBody(
                                [
                                    dcc.Graph(id='hospitals_donut'),
                                ],
                                 
                            )
                        ], style={'backgroundColor': '#60B3F7', 'margin-bottom':'10px'}),

                        dbc.Card([
                            dbc.CardHeader(html.H4(id='donut_title', children="Dengue Cases/Deaths per Island Group", style={'color': '#FFFFFF'})),
                            dbc.CardBody([
                                dcc.Graph(id='pie-graph'),
                                dcc.Store(id='metric-store', data='Cases')
                            ])
                        ], style={'backgroundColor': '#60B3F7'}),

    
                    ],
                    width=6,
                    style={'height': '900px'}
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4(id ='choro_title', children="Dengue Cases/Deaths by Region", style={'color': '#FFFFFF'})),
                        dbc.CardBody(dcc.Graph(id='choropleth-with-hospitals', config={"scrollZoom": True} ))
                    ], style={'backgroundColor': '#60B3F7'}),
                    width=6
                )
            ], className="mt-4"),

            # Buttons Row
            dbc.Row(
                dbc.Col(
                    dbc.ButtonGroup([
                        dbc.Button("Cases", color="warning", id='cases_button', n_clicks=0,
                                   style={'backgroundColor': '#60B3F7', 'borderColor': '#FFFFFF', 'color': '#FFFFFF'}),
                        dbc.Button("Deaths", color="danger", id='deaths_button', n_clicks=0,
                                   style={'backgroundColor': '#EC7777', 'borderColor': '#FFFFFF', 'color': '#FFFFFF'}),
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
                                inline=True,  # Keeps the checkboxes inline (horizontal)
                                style={
                                    'backgroundColor': '#393D3F',  # Dark 
                                    'color': '#FFFFFF',  # White
                                    'display': 'flex',  
                                    'flexWrap': 'wrap', 
                                    'padding': '10px',
                                      
                                  
                                },
                                inputStyle={"margin-right": "10px", "margin-bottom": "10px"},  # Space checkboxes
                                labelStyle={'margin-right': '10px', 'margin-bottom': '10px'}  # Space labels
                            ),
                            dcc.Graph(
                                    id='region-graph'
                                ),
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
                    ], style={'backgroundColor': '#60B3F7'}),
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
                                style={'backgroundColor': '#FFFFFF', 'color': '#393D3F'}
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
                    ], style={'backgroundColor': '#60B3F7'}),
                    width=12
                ),
                className="mt-4 mb-4"
            )
        ]#,fluid=True
        ),dcc.Interval(id='interval-trigger', interval=60000, n_intervals=0) #serve as input for the hospital donut
    ]
)


# --------------------------Callbacks-------------------------------------------------------------------------------------------------------------------------
#for updating the card headers for choropleth and donut chsart
@app.callback(
    [Output('donut_title', 'children'),
     Output('choro_title', 'children')],
    Input('metric-store', 'data')
)
def update_titles(metric):
    if metric == "Cases":
        donut_title = "Dengue Cases per Island Group"
        choro_title = "Dengue Cases by Region and Hospital Locations"
    else:  # metric == "Deaths"
        donut_title = "Dengue Deaths per Island Group"
        choro_title = "Dengue Deaths by Region and Hospital Locations"
    
    return donut_title, choro_title

#donut chart for number of hospitals per island
@app.callback(
    Output('hospitals_donut', 'figure'),
    Input('interval-trigger', 'n_intervals'),

)
#HORIZONTAL HOSPITAL BAR, NOT DONUT ANYMORE
def update_hospital_donut(_):
    island_colors = {
        "Luzon": '#FFD700',
        "Visayas": "#60B3F7",
        "Mindanao" : "#EC7777"
    }
    
    fig = px.bar(
        hospitals_per_island,
        x="Hospital_Count",
        y="Island",
        orientation='h',  # Horizontal bar chart
        color='Island',
        color_discrete_map=island_colors
    )

    fig.update_traces(
        texttemplate='%{x}',  
        textposition='outside'
    )

    fig.update_layout(
        paper_bgcolor='#393D3F',
        plot_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        #margin=dict(l=50, r=50, t=50, b=50),
        yaxis=dict(title="Island"),
        xaxis=dict(title="Hospital Count",range=[0, max(hospitals_per_island['Hospital_Count']) + 50],),
        #width=600,
        #height=600,  
        bargap=0.2  
    )

    return fig

# FOR PIE AND CHOROPLETH ROW
    #BuTTONS
@app.callback(
    Output('metric-store', 'data'),
    [Input('cases_button', 'n_clicks'),
     Input('deaths_button', 'n_clicks')],
    [State('metric-store', 'data')]
)

def update_metric(cases_n_clicks, deaths_n_clicks, last_clicked_metric):
    cases_n_clicks = cases_n_clicks or 0
    deaths_n_clicks = deaths_n_clicks or 0

    if cases_n_clicks > deaths_n_clicks and last_clicked_metric != 'Cases':
        return 'Cases'
    if deaths_n_clicks > cases_n_clicks and last_clicked_metric != 'Deaths':
        return 'Deaths'

    return last_clicked_metric



# Update pie chart based on button
@app.callback(
    Output('pie-graph', 'figure'),
    Input('metric-store', 'data')
)
def update_pie_chart(metric):
    values = 'Dengue_Cases' if metric == 'Cases' else 'Dengue_Deaths'
    #title = f'Dengue {metric} per Island'
    

    island_colors = {
        "Luzon": '#FFD700',
        "Visayas": "#60B3F7",
        "Mindanao" : "#EC7777"
    }
    

    fig = px.pie(
        df,
        names='Island',
        values=values,
        hole=0.5,
        
        color='Island',
        color_discrete_map=island_colors
    )
    fig.update_traces(textinfo='percent+label')

    fig.update_layout(
        paper_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        width=600,
        #height=600,
    )
    return fig

# Update choropleth map based on button
@app.callback(
    Output('choropleth-with-hospitals', 'figure'),
    Input('metric-store', 'data')
)
def update_choropleth(metric):
    metric_column = 'Dengue_Cas' if metric == 'Cases' else 'Dengue_Dea'
    
    # color based on meteric
    if metric == 'Cases':
        color_scale = [
            [0.0, '#FFFFFF'],  # White for the minimum
            [1.0, '#60B3F7']   # Blue for the maximum (Cases)
        ]
    elif metric == 'Deaths':
        color_scale = [
            [0.0, '#FFFFFF'],  # White for the minimum
            [1.0, '#DC143C']   # Red for the maximum (Deaths)
        ]
    
    # choropleth map
    fig = px.choropleth_mapbox(
        total_cases_and_deaths_with_region,
        geojson=total_cases_and_deaths_with_region.__geo_interface__,
        locations=total_cases_and_deaths_with_region.index,
        color=metric_column,
        hover_name='Region',
        mapbox_style="carto-darkmatter",  # dark map
        zoom=5.1,
        center={"lat": 12.8797, "lon": 121.9740},
        opacity=0.7,
        color_continuous_scale=color_scale,  
        #title=f"Dengue {metric} by Region"
        
    )

    # Add hospital points with the ye llowcolor
    fig.add_scattermapbox(
        lat=hospitals_and_clinics['lat'],
        lon=hospitals_and_clinics['lon'],
        mode='markers',
        marker=dict(size=5, color='#FFD700', opacity=0.7),  
        text=hospitals_and_clinics['name'],
        hoverinfo="text",
    )

    # Update layout
    fig.update_layout(
        paper_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        title=dict(font=dict(size=20, color='#FFFFFF')),
        coloraxis_colorbar=dict(
            title=f"Dengue {metric}",  
            x=0.99,  
            y=0.8,   
            xanchor='right',  
            yanchor='middle',  
            len=0.4,  
            bgcolor="rgba(0,0,0,0.5)"  
        ),
        legend=dict(font=dict(color='#FFFFFF')),
        width=600,
        height=1000,
        margin=dict(l=0, r=0, t=0, b=0),
        
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
        # no region selected
        return go.Figure(
            data=[],
            layout=go.Layout(
                title=dict(
                    text="No Region Selected",
                    font=dict(size=20, color='#FFFFFF'),  # Title font color and size
                    x=0.5,  # Center title
                    xanchor='center'
                ),
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    title="Region",
                    linecolor='#FFFFFF',
                    gridcolor='#60B3F7',
                    zeroline=False,
                ),
                yaxis=dict(
                    title="Count",
                    linecolor='#FFFFFF',
                    gridcolor='#60B3F7',
                    zeroline=False,
                ),
            )
        )

    # Filter the data based on  regions and year range
    filtered_df = df[(df["Region"].isin(regions)) & (df["Year"].between(years[0], years[1]))]

    if filtered_df.empty:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="No Data Available for Selected Regions and Years",
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    title="Region",
                    linecolor='#FFFFFF',
                    gridcolor='#60B3F7',
                    zeroline=False,
                ),
                yaxis=dict(
                    title="Count",
                    linecolor='#FFFFFF',
                    gridcolor='#60B3F7',
                    zeroline=False,
                ),
            )
        )

    filtered_df = filtered_df.groupby(['Region', 'Year'], as_index=False).sum()

    # Dynamically change titles
    if len(regions) <=3: #lmao 
        # If 1 to 3 regions are selected, list the region names
        title = f"Cases and Deaths in {', '.join(regions)} from {years[0]} to {years[1]}"
    else:
        # If more than 3 regions are selected, use "Multiple Regions" in the title
        title = f"Cases and Deaths in selected regions from {years[0]} to {years[1]}"

    # Create a stacked bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df['Region'],
        y=filtered_df['Dengue_Cases'] - filtered_df['Dengue_Deaths'],  # Non-death cases
        name='Dengue Cases (Excluding Deaths)',
        marker_color='#C7E5FF'  # Teal
    ))

    fig.add_trace(go.Bar(
        x=filtered_df['Region'],
        y=filtered_df['Dengue_Deaths'],  # Deaths
        name='Dengue Deaths',
        marker_color='#EC7777'  # Red
    ))

    fig.update_layout(
        barmode='stack',  # Stacked barschat
        title=dict(
            text=title,  
            font=dict(size=20, color='#FFFFFF'),  # Title font color and size
            x=0.5,  # Center the title
            xanchor='center'
        ),
        paper_bgcolor='#393D3F',
        plot_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        xaxis=dict(
            title=dict(text="Region", font=dict(color='#FFFFFF')),
            linecolor='#FFFFFF',
            gridcolor='#60B3F7'
        ),
        yaxis=dict(
            title=dict(text="Count", font=dict(color='#FFFFFF')),
            linecolor='#FFFFFF',
            gridcolor='#60B3F7'
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
                title=dict(
                    text="No Region Selected",
                    font=dict(size=20, color='#FFFFFF'), 
                    x=0.5,  # Center 
                    xanchor='center'  # Anchor 
                ),
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#60B3F7'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#60B3F7'),
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
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#60B3F7'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#60B3F7'),
            )
        )

    aggregated_df = filtered_df.groupby(['Date'], as_index=False).sum()

    # Create traces for cases and deaths
    cases_trace = go.Scatter(
        x=aggregated_df['Date'],
        y=aggregated_df['Dengue_Cases'],
        name='Dengue Cases',
        mode='lines',
        line=dict(color='#C7E5FF'),
        yaxis='y1'
    )

    deaths_trace = go.Scatter(
        x=aggregated_df['Date'],
        y=aggregated_df['Dengue_Deaths'],
        name='Dengue Deaths',
        mode='lines',
        line=dict(color='#EC7777'),
        yaxis='y2'
    )

    # Create the figure
    fig = go.Figure(data=[cases_trace, deaths_trace])

    # Update the layout for dual y-axes
    fig.update_layout(
        title=dict(
            text=f'Dengue Cases and Deaths Over Time in {selected_region}',
            font=dict(size=20, color='#FFFFFF'),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='#393D3F',
        plot_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        xaxis=dict(
            title=dict(text="Date", font=dict(color='#FFFFFF')),
            linecolor='#FFFFFF',
            gridcolor='#60B3F7'
        ),
        yaxis=dict(
            title=dict(text="Number of Cases", font=dict(color='#C7E5FF')),
            linecolor='#C7E5FF',
            gridcolor='#60B3F7',
        ),
        yaxis2=dict(
            title=dict(text="Number of Deaths", font=dict(color='#EC7777')),
            overlaying='y',  # Overlay y-axis on the same plot
            side='right',    # Position it on the right
        ),
        legend=dict(font=dict(color='#FFFFFF')),
        hovermode='x unified'
    )
    
    return fig

def update_specific_region_graph_old(selected_region, selected_years):
    if not selected_region:
        return go.Figure(
            data=[], 
            layout=go.Layout(
                title=dict(
                    text="No Region Selected",
                    font=dict(size=20, color='#FFFFFF'), 
                    x=0.5,  # Center 
                    xanchor='center'  # Anchor 
                ),
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#60B3F7'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#60B3F7'),
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
                paper_bgcolor='#393D3F',
                plot_bgcolor='#393D3F',
                font=dict(color='#FFFFFF'),
                xaxis=dict(title="Date", linecolor='#FFFFFF', gridcolor='#60B3F7'),
                yaxis=dict(title="Number of Cases/Deaths", linecolor='#FFFFFF', gridcolor='#60B3F7'),
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
        color_discrete_map={'Dengue_Cases': '#C7E5FF', 'Dengue_Deaths': '#EC7777'}
    )

    fig.update_layout(
        paper_bgcolor='#393D3F',
        plot_bgcolor='#393D3F',
        font=dict(color='#FFFFFF'),
        title=dict(
            font=dict(size=20, color='#FFFFFF'),  # Title font color and size
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title at the center
        ),
        xaxis=dict(title=dict(text="Date", font=dict(color='#FFFFFF')), linecolor='#FFFFFF', gridcolor='#60B3F7'),
        yaxis=dict(title=dict(text="Number of Cases/Deaths", font=dict(color='#FFFFFF')), linecolor='#FFFFFF', gridcolor='#60B3F7'),
        legend=dict(font=dict(color='#FFFFFF')),
        hovermode='x unified',
    )
    return fig


# ------------------------------------------run app ------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
