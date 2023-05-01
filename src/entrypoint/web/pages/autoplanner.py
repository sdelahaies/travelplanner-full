import dash
from dash import html, dcc, callback, State, Output, Input, ALL, ctx
from flask_login import current_user
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import requests


from src.entrypoint.web.pages.utils import *

dash.register_page(__name__,path="/autoplanner")

API_URL = "https://api-adresse.data.gouv.fr/search/?q="

def layout():
    if current_user.is_authenticated == False:
        return dcc.Location(pathname="/login", id="location")

    searchBar = html.Div( 
                dbc.InputGroup(
                    [
                        dbc.Input(id="input-searchBar", placeholder="Type location"),
                        dbc.Button("Search", id="input-searchBtn",color="primary"),
                    ]
                ))


    destCard = dbc.Card(
                    html.Div(dbc.Col(
                            html.H6(html.B(id ='dest-alert',children ="Destination: ")),
                            align='center'),style={'margin':'10px', "padding-top": "5px"}
                        ),style={'margin-top':'20px','margin-bottom':'20px'}
    )
    
    autoMap = html.Div(dbc.Row(
                        dl.Map(
                            id="auto-map", 
                            children=[
                                dl.TileLayer(),
                                dl.GeoJSON(id="dest-markers",zoomToBounds=True, format="geojson"),
                                dl.GeoJSON(id="poi_markers")
                                ],zoom=5,center=(46, 1.5),), 
                        style={
                            'height': '65vh',
                            'margin-top': '10px',
                            'margin-bottom': '10px',
                            'display': 'flex'
                        }, justify="center"))

    parameters = dbc.Card(
                    [html.Div([
                        dbc.Label("Select the data source"),
                        dbc.RadioItems(
                            options=[
                                {"label": "datatourisme", "value": 1},
                                {"label": "opentripmap", "value": 2},
                            ],
                            value=1,
                            id="data-source",
                            inline=True,
                        ),
                        dbc.Label("Select activity type (leave blank to select all)"),
                        dcc.Dropdown(id="dropdown-kind", 
                            options=["tout","restaurants","hotels","sites culturels","randonnées","événements"], 
                            placeholder="Select activity type ",multi=True,style={'color': 'black'}),
                    ],style={'margin-left': '10px','margin-right': '10px','margin-top':'10px','margin-bottom':'10px'})
                ])

    preferences = dbc.Row([
                    dbc.Button(children="Preferences", id="pref-button",color='primary',
                               style={'margin-top':'10px','margin-left':'10px','margin-right':'10px','margin-bottom':'10px'}),
                    dbc.Collapse(
                        parameters,
                        id="pref-collapse",
                        is_open=False,
                        )
                    ],justify = 'center',
                    style={'margin-top':'10px','margin-left':'10px','margin-right':'10px'}
                    )


    searchPois_Btn = html.Div(
                    dbc.Row(
                        dbc.Button(id="searchPois-btn",children = "Find points of interest",color='primary'),
                        justify= "center"),
                        style={'margin-top':'10px','margin-left':'20px','margin-right':'20px'}
                    )
    
    plannerBtn = html.Div(
                dbc.Row(
                    dbc.Button(id="planner-btn",children = "Let's plan our tour!",color='primary'),
                    justify= "center"),
                    style={'margin-top':'20px','margin-bottom':'20px','margin-left':'20px','margin-right':'20px'}
                )
    
    day_planner = html.Div(id="dayPlanner",children="",
                       style={'margin-top': '10px','margin-bottom': '10px',"maxHeight": "600px", "overflow": "scroll"})

    return dbc.Container(
        [   
            html.H2(html.B("Auto-Planner"), style={"margin-bottom": "30px"}),
            searchBar,
            destCard,
            dbc.Row([
                dbc.Col([preferences,
                         searchPois_Btn,
                         plannerBtn,
                         day_planner],width = {'size':4}),       
                dbc.Col(autoMap,width = {'size':8})
            ])
        ],
        fluid=False,
    )  
    
    

@callback(
    [Output('dest-alert','children'),
     Output('searchPois-btn','value')],
    Input("dest-markers", "click_feature"),
    )
def select_dest(point):
    if point is None:
        raise PreventUpdate
    print("Destination: "+point["properties"]["label"]+', '+point["properties"]["context"])
    return ["Destination: "+point["properties"]["label"]+', '+point["properties"]["context"]],point["geometry"]["coordinates"]
    
@callback(
    Output("dest-markers", "data"),
    Input("input-searchBtn", "n_clicks"),
    State("input-searchBar", "value"))
def launch_search_loc(click,value):
    if value is None or click is None:
        raise PreventUpdate
    url = "{url}{place}".format(url=API_URL, place=value)
    headers = {'Content-Type': 'application/geojson'}
    response = requests.get(url, headers=headers)
    print(response.request.url)
    return response.json()

@callback(
    Output("pref-collapse", "is_open"),
    [Input("pref-button", "n_clicks")],
    [State("pref-collapse", "is_open")],)
def collapse_pref(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("dropdown-kind", "options"),
    Output("dropdown-kind", "value"),
    Input("data-source","value"),
)
def update_kind(source):
    if source==1:
        return ["tout","restaurants","hotels","sites culturels","randonnées","événements"],None
    elif source ==2:
        return ["historic","industrial_facilities","natural","cultural","religion","foods","architecture","accomodations","amusements"],None

@callback(
    [Output("poi_markers", "children"),
     Output("auto-map","bounds")],
    [Input("searchPois-btn", "n_clicks"),
     Input("searchPois-btn", "value")],   # set as state otherwise it updates each time you change destination
     [State("data-source","value"),
     State("dropdown-kind","value")]
)
def query_poi_mod(click,coords,source,kinds):
    if not click:
        raise PreventUpdate
    if coords is None:
        return
    lat = coords[0]
    lon = coords[1]
    if source == 1:
        data=query_datatourisme(lat,lon,kinds)
        markers, bounds = poi_to_marker_2(data,source)
    if source == 2:
        data=query_opentripmap(lat,lon,kinds)
        markers, bounds = poi_to_marker_2(data,source)
    return markers,bounds

@callback(
    Output("dayPlanner", "children"),
    Input("planner-btn", "n_clicks"),
    State("poi_markers","data"),
    State("data-source","value"))
def make_travel(click,markers,source):
    if click:
        if source == 1:
            pois = pd.read_csv("request_dt.csv")
            return kmeans_plan_dt(pois)
        elif source == 2:
            pois = pd.read_csv("request_otm.csv")
            return kmeans_plan_otm(pois)