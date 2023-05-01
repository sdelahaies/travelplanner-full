import dash
from dash import html, dcc, callback, State, Output, Input, ALL, ctx
from flask_login import current_user
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import requests
import dash_leaflet.express as dlx
import random

from src.entrypoint.web.pages.utils import *

dash.register_page(__name__,path="/history")

API_URL = "https://api-adresse.data.gouv.fr/search/?q="

def layout():
    if current_user.is_authenticated == False:
        return dcc.Location(pathname="/login", id="location")
    
    autoMap = html.Div(dbc.Row(
                        [
                            dl.Map(
                                id="auto-map_3", 
                                children=[
                                    dl.TileLayer(),
                                    dl.GeoJSON(id="poi_markers_3",zoomToBounds=True, format="geojson")
                                ],
                                zoom=5,
                                center=(46, 1.5),
                            ),
                            dbc.Button(id="button-load-history", n_clicks=0, style={"visibility": "hidden"}),
                        ], 
                        style={
                            'height': '85vh',
                            'margin-top': '10px',
                            'margin-bottom': '10px',
                            'display': 'flex'
                        }, justify="center"))
    
    poiCard = dbc.Card(
                        id ='poi-card-history',
                        children=[
                            html.B(children="Point of interest:"),
                            html.P(id="poi-test-history",children="..."),
                            dcc.Store(id='poi-value-history'),                          
                        ],
                        style={'margin':'10px 0px 30px 0px', "padding": "15px"}
                    )
    
    Cart = html.Div([
            dbc.Card(
                dbc.CardBody([
                        dbc.Row(
                            [
                                dbc.Label(id = "cart-label-history",children= "History list", width=7, style={"font-size": "18px"}),
                            ],
                        ),
                    ],
                    style={"padding": "14px"}
                ),
                className="mb-3",
                style={"margin": "0px"}
            ),
            dbc.Row([
                dbc.Col(
                    [
                        html.Div(id="cart-history"),
                        dcc.Store(id="cart-value-history"),
                    ],
                    width=12,
                ),
            ]),
        ])
    
    return dbc.Container(
        [   
            html.H2(html.B("Planner History"), style={"margin-bottom": "30px"}),
            dbc.Row([
                dbc.Col(
                    [
                        poiCard,
                        Cart
                    ],
                    width={'size':4}
                ),
                dbc.Col(autoMap, width={'size':8})
            ])
        ],
        fluid=False,
    )  

@callback(
    [
        Output("poi_markers_3", "data"),
        Output('cart-value-history', 'data'),
    ],
    Input("button-load-history", "n_clicks"),
)
def query_poi_planner(n):
    data=query_history()
    pois=pois_to_dict(data["response"])

    return [pois, pois["features"]]
    
@callback(
    [
        Output("poi-test-history", "children"),
        Output("poi-value-history", "data"),
    ],
    Input("poi_markers_3", "click_feature")
)
def click_on_poi(point):
    if point is None:
        raise PreventUpdate
    return [point["tooltip"], point]

@callback(
    Output("cart-history", "children"),
    [
        Input('cart-value-history', 'data'),
    ],
)
def update_cart(lists):
    print("lists", lists)
    if lists is not None:
        response = []
        
        for point in lists:
            
            card = dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Name", width=12),
                                dbc.Label(point["tooltip"], width=12),
                            ],
                        ),
                    ]
                ),
                style={"width": "100%"},
                className="mb-3",
            )

            response.append(card)

        return response