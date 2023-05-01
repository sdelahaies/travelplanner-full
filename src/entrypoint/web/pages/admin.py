import dash
from dash import html, dcc
from flask_login import current_user
import dash_bootstrap_components as dbc

dash.register_page(__name__)

def layout():
    if current_user.is_authenticated == False:
        return dcc.Location(pathname="/login", id="location")
    
    if current_user.role == "user":
        return dcc.Location(pathname="/login", id="location")

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
                                            html.Div(html.H3("Admin")),
                                            html.Br(),
                                        ]
                                    )
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