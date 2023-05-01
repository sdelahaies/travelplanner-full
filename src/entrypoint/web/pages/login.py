
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.Div(
                                    [
                                        html.H3("Login", id="h1"),
                                    ],
                                    className="mb-3",
                                ),
                                html.Div(
                                    [
                                        dbc.Label("Username", html_for="uname-box"),
                                        dbc.Input(placeholder="Enter your username", type="text", id="uname-box"),
                                    ],
                                    className="mb-3",
                                ),
                                html.Div(
                                    [
                                        dbc.Label("Password", html_for="pwd-box"),
                                        dbc.Input(placeholder="Enter your password", type="password", id="pwd-box"),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Button(children="Login", n_clicks=0, type="submit", id="login-button", className="mt-5"),
                                html.Div(children="", id="output-state", className="mt-5 mb-3"),
                                html.Br(),
                                dcc.Link("Go to the Home page", href="/"),
                            ],
                            style={
                                "margin": "100px",
                                "padding": "50px"
                            }
                        ),
                    ],
                    width=12,
                ),
            ],
        ),
    ],
    fluid=False,
) 
