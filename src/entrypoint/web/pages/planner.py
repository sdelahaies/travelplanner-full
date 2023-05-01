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

dash.register_page(__name__,path="/planner")

API_URL = "https://api-adresse.data.gouv.fr/search/?q="

def layout():
    if current_user.is_authenticated == False:
        return dcc.Location(pathname="/login", id="location")

    searchBar = html.Div( 
                dbc.InputGroup(
                    [
                        dbc.Input(id="input-searchBar_0", placeholder="Type location"),
                        dbc.Button(id="input-searchBtn_0",children="Search",color="primary"),
                    ]
                ))


    destCard = dbc.Card(
                    html.Div(dbc.Col(
                            html.H6(html.B(id ='dest-alert_0',children ="Destination: ")),
                            align='center'),style={'margin':'10px', "padding-top": "5px"}
                        ),style={'margin-top':'20px','margin-bottom':'20px'}
    )
    
    autoMap = html.Div(dbc.Row(
                        dl.Map(
                            id="auto-map_0", 
                            children=[
                                dl.TileLayer(),
                                dl.GeoJSON(id="dest-markers_0",zoomToBounds=True, format="geojson"),
                                dl.GeoJSON(id="poi_markers_0",zoomToBounds=True, format="geojson")
                                ],zoom=5,center=(46, 1.5),), 
                        style={
                            'height': '85vh',
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
                            id="data-source_0",
                            inline=True,
                        ),
                        dbc.Label("Select activity type (leave blank to select all)"),
                        dcc.Dropdown(id="dropdown-kind_0", 
                            options=["tout","restaurants","hotels","sites culturels","randonnées","événements"], 
                            placeholder="Select activity type ",multi=True,style={'color': 'black'}),
                    ],style={'margin-left': '10px','margin-right': '10px','margin-top':'10px','margin-bottom':'10px'})
                ])

    preferences = dbc.Row([
                    dbc.Button(children="Preferences", id="pref-button_0",color='primary',
                               style={'margin-top':'10px','margin-left':'10px','margin-right':'10px','margin-bottom':'10px'}),
                    dbc.Collapse(
                        parameters,
                        id="pref-collapse_0",
                        is_open=False,
                        )
                    ],justify = 'center',
                    style={'margin-top':'10px','margin-left':'10px','margin-right':'10px'}
                    )

    searchPois_Btn = html.Div(
                    dbc.Row(
                        dbc.Button(id="searchPois-btn_0",children = "Find points of interest",color='primary'),
                        justify= "center"),
                        style={'margin-top':'10px','margin-left':'20px','margin-right':'20px','margin-bottom':'10px'}
                    )
    
    poiCard = dbc.Card(
                        id ='poi-card',
                        children=[
                            html.B(children="Point of interest:"),
                            html.P(id="poi-test",children="..."),
                            dcc.Store(id='poi-value'),
                            dbc.Button("Add to cart", id="button-add-cart", n_clicks=0)                                
                        ],
                        style={'margin':'20px 5px', "padding": "15px"}
                    )
    
    Cart = html.Div([
            dbc.Card(
                dbc.CardBody([
                        dbc.Row(
                            [
                                dbc.Label(id = "cart-label",children= "Cart", width=7, style={"font-size": "18px"}),
                                dbc.Button("Save", id="button-save-cart", n_clicks=0, style={"width": "75px", "margin-right": "10px"}),
                                dbc.Button("Delete", id="button-delete-cart", n_clicks=0, style={"width": "75px"}),
                            ],
                        ),
                    ],
                    style={"padding": "14px"}
                ),
                className="mb-3",
                style={"margin": "5px"}
            ),
            dbc.Row([
                dbc.Col(
                    [
                        html.Div(id="cart"),
                        dcc.Store(id='cart-value', storage_type='session'),
                        html.Div(id="cart-itinerary"),
                    ],
                    width=12,
                ),
            ]),
        ])
    
    return dbc.Container(
        [   
            html.H2(html.B("Planner"), style={"margin-bottom": "30px"}),
            searchBar,
            destCard,
            dbc.Row([
                dbc.Col(
                    [
                        preferences,
                        searchPois_Btn,
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
    [Output('dest-alert_0','children'),
     Output('searchPois-btn_0','value')],
    Input("dest-markers_0", "click_feature"),
    )
def select_dest(point):
    if point is None:
        raise PreventUpdate
    
    return ["Destination: "+point["properties"]["label"]+', '+point["properties"]["context"]],point["geometry"]["coordinates"]
    
@callback(
    Output("dest-markers_0", "data"),
    Input("input-searchBtn_0", "n_clicks"),
    State("input-searchBar_0", "value"))
def launch_search_loc(click,value):
    if value is None or click is None:
        raise PreventUpdate
    
    url = "{url}{place}".format(url=API_URL, place=value)
    headers = {'Content-Type': 'application/geojson'}
    response = requests.get(url, headers=headers)
    print(response.request.url)
    print("----------------------------------------")
    print(response.json())

    return response.json()

@callback(
    Output("pref-collapse_0", "is_open"),
    [Input("pref-button_0", "n_clicks")],
    [State("pref-collapse_0", "is_open")],)
def collapse_pref(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("dropdown-kind_0", "options"),
    Output("dropdown-kind_0", "value"),
    Input("data-source_0","value"),
)
def update_kind(source):
    if source==1:
        return ["tout","restaurants","hotels","sites culturels","randonnées","événements"],None
    elif source ==2:
        return ["historic","industrial_facilities","natural","cultural","religion","foods","architecture","accomodations","amusements"],None

@callback(
    [Output("poi_markers_0", "data")],
    [
        Input("searchPois-btn_0", "n_clicks"),
        Input("searchPois-btn_0", "value")],   # set as state otherwise it updates each time you change destination
    [
        State("data-source_0","value"),
        State("dropdown-kind_0","value")
    ]
)
def query_poi_planner(click,coords,source,kinds):
    if not click:
        raise PreventUpdate
    if coords is None:
        return
    print('-----------------------------------------------')
    print('test 1:',coords)
    lat = coords[0]
    lon = coords[1]
    if source == 1:
        print(source)
        data=query_datatourisme_planner(lat,lon,kinds)
        pois=pois_to_dict(data["response"])
    elif source == 2:
        print(source)
        pois=query_opentripmap_planner(lat, lon, kinds)

    return [pois]
    
@callback(
    [
        Output("poi-test", "children"),
        Output("poi-value", "data"),
    ],
    Input("poi_markers_0", "click_feature")
)
def click_on_poi(point):
    if point is None:
        raise PreventUpdate
    return [point["tooltip"], point]

@callback(
    [
        Output('cart-value', 'data'),
        Output("button-delete-cart", "n_clicks")
    ],
    [
        Input("button-add-cart", "n_clicks"),
        Input("poi-value", "data"),
        State("cart-value", "data"),
        Input({'type': 'order-item-cart', 'index': ALL}, 'value'),
        Input({'type': 'rating-item-cart', 'index': ALL}, 'value'),
    ],
)    
def handle_cart(n, point, cart, order, ratings):
    triggered_id = ctx.triggered_id
    if triggered_id is None:
        raise PreventUpdate
    
    response = None
    if triggered_id == "button-add-cart":
        response = add_poi_to_cart(point, cart)
    elif triggered_id.get("type", None) is not None and triggered_id.type == "order-item-cart":
        response = cart_drop(cart)
    elif triggered_id.get("type", None) is not None and triggered_id.type == "rating-item-cart":
        response = cart_rating(cart)

    if response is None:
        raise PreventUpdate   
    
    return [response, 0]

@callback(
    Output("cart", "children"),
    [
        Input('cart-value', 'data'),
        Input("button-add-cart", "n_clicks"),
    ],
)
def update_cart(lists, n):
    if lists is not None:
        response = []
        options = [{'label': i, 'value': i} for i, p in enumerate(lists)]
        options_ratings = [{'label': i, 'value': i} for i in range(1, 6)]
        for index, point in enumerate(lists):
            rating = 4
            if point.get("rating", None) is not None:
                rating = point["rating"]
            card = dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Name", width=12),
                                dbc.Label(point["tooltip"], width=12),
                            ],
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Order", width=12),
                                        dcc.Dropdown(
                                            options=options,
                                            id={
                                                'type': 'order-item-cart',
                                                'index': index
                                            },
                                            value=index,
                                            multi=False,
                                            style={"color": "black"}
                                        )
                                    ],
                                    width=12
                                )
                            ],
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Rating", width=12),
                                        dcc.Dropdown(
                                            options=options_ratings,
                                            id={
                                                'type': 'rating-item-cart',
                                                'index': index
                                            },
                                            value=rating,
                                            multi=False,
                                            style={"color": "black"}
                                        )
                                    ],
                                    width=12
                                )
                            ],
                        ),
                    ]
                ),
                style={"width": "100%"},
                className="mb-3",
            )

            response.append(card)

        return response

@callback(
    Output('cart-value', 'clear_data'),
    [Input("button-delete-cart", "n_clicks")],
)
def delete_cart(n):
    if n == 0:
        raise PreventUpdate

    if n > 0:
        return []


@callback(
    Output("button-save-cart", "n_clicks"),
    [
    Input("button-save-cart", "n_clicks"),
    State("cart-value", "data"),
    ],
)
def save_cart_history(n, cart):
    if n == 0:
        raise PreventUpdate
    
    list_ids = []
    for item in cart:
        list_ids.append({"id": item["id"], "rating": item.get("rating", 4)})

    query_save_cart_planner(list_ids)

    return 0

"""
#test
def add_poi_to_cart(point, store):
    if point is not None:
        if store is None:
            store = []
        store.append(point)
        return store

@callback(
    [Output('cart-value', 'data'),
    Output("button-delete-cart", "n_clicks")],
    [
        Input("button-add-cart", "n_clicks"),
        Input("poi-value", "data"),
        State("cart-value", "data"),
        Input({'type': 'order-item-cart', 'index': ALL}, 'value'),
    ],
)    
def handle_cart(n, point, cart, order):
    triggered_id = ctx.triggered_id
    if n == 0:
        raise PreventUpdate
    response = None
    if triggered_id == "button-add-cart":
        response = add_poi_to_cart(point, cart)
    #elif triggered_id.type is not None and triggered_id.type == "order-item-cart":
    #    response =  itinerary_cart_drop(cart)
    if response is None:
        raise PreventUpdate   
    return [response, 0]
"""


"""       
@callback(
    Output("cart", "children"),
    [
        Input('cart-value', 'data'),
    ],
)
def update_cart(lists):
    if lists is not None:
        response = []
        options = [{'label': i, 'value': i} for i, p in enumerate(lists)]
        for index, point in enumerate(lists):
            card = dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Name", width=3),
                                dbc.Label(point["properties"]["name"], width=9),
                    
                            ],
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Order"),
                                    ],
                                    width=3
                                ),
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            options=options,
                                            id={
                                                'type': 'order-item-cart',
                                                'index': index
                                            },
                                            value=index,
                                            multi=False,
                                            style={"color": "black"}
                                        )
                                    ],
                                    width=9
                                )
                            ],
                        ),
                    ]
                ),
                style={"width": "100%"},
                className="mb-3",
            )

            response.append(card)
        return response
"""   
    
    
"""
@callback(
    Output('cart-value', 'clear_data'),
    [Input("button-delete-cart", "n_clicks")],
)
def delete_cart(n):
    if n == 0:
        raise PreventUpdate

    if n > 0:
        return []
    
@callback(
    Output("geojson_itinerary", "chidren"),
    [
    Input("button-itinerary-cart", "n_clicks"),
    State('cart-value', 'data'),
    ],
)
def itinerary_cart(n, cart):
    if n == 0:
        raise PreventUpdate

    if n > 0:
        itinerary = []
        for item in cart:
            itinerary_item = item["geometry"]["coordinates"]
            itinerary.append(itinerary_item)

        return route_itinerary(itinerary)




def itinerary_cart_drop(cart):
    if cart is None:
        raise PreventUpdate

    index = ctx.triggered_id.index
    move_to_index = ctx.triggered[0]["value"]

    if cart is not None:
        # Change position of this element in the itinerary carts
        cart_np_array = np.array(cart)

        value = cart_np_array[index]

        cart_np_array = np.delete(cart_np_array, index)
        cart_np_array = np.insert(cart_np_array, move_to_index, value)
    
        print("itinerary_drop cart", cart)
        print("itinerary_drop new cart", cart_np_array)

        return cart_np_array

def route_itinerary(poi_cart, profile = "car"):


    base_url = "https://api.mapbox.com/directions/v5/mapbox/"
    map_box_token = "pk.eyJ1IjoiaW1hZG4iLCJhIjoiY2xmOXdpYjR2MXRpNzQwbzR5b2s0ZG1zYSJ9.X-IlClUq7P4bG6jr4JVyEA"
    tranportation_mode = {"walk":"walking/", "cycle" :"cycling/","car": "driving/"}
    
    poi_coordinates = ""
    for point in poi_cart:
        # poi_cordinates += str(point[0])+","+str(point[1])+";"
        poi_coordinates += "{lon},{lat};".format(lon=str(point[0]), lat=str(point[1]))
    
    poi_coordinates = poi_coordinates[:-1]

    # URL = base_url+tranportation_mode[profile]+poi_cordinates+"?"+"&steps=true"+"&geometries=geojson"+"&access_token="+map_box_token
    URL = "{base_url}{tranportation_mode}{poi_coordinates}?&steps=true&geometries=geojson&access_token={map_box_token}".format(
        base_url = base_url,
        tranportation_mode = tranportation_mode[profile],
        poi_coordinates = poi_coordinates,
        map_box_token = map_box_token
    )

    itinerary = (requests.get(URL)).json()

    return itinerary["waypoints"]
"""