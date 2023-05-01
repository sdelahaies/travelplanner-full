
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

def layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    html.Div(
                                        [
                                            html.Div(html.H3("Planner Mode")),
                                            html.Br(),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(html.H6("This mode allows you to search for points of interest by location and to save them on your profile.")),
                                            html.Br(),
                                            dbc.Button("Go to Planner", href="/planner", id="button-planner-home", n_clicks=0),
                                        ]
                                    )
                                ],
                                style={
                                    "margin": "100px",
                                    "padding": "50px"
                                }
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    html.Div(
                                        [
                                            html.Div(html.H3("Auto-Planner Mode ")),
                                            html.Br(),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(html.H6("This mode allows you to search for points of interest by location and produces daily travel plans.")),
                                            html.Br(),
                                            dbc.Button("Go to Auto-Planner", href="/autoplanner", id="button-autoplanner-home", n_clicks=0),
                                        ]
                                    )
                                ],
                                style={
                                    "margin": "100px",
                                    "padding": "50px"
                                }
                            ),
                        ],
                        width=6,
                    ),
                ],
            ),
        ],
        fluid=False,
    )