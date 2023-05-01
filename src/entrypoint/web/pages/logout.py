import dash
from dash import html, dcc
from flask_login import logout_user, current_user
import dash_bootstrap_components as dbc

dash.register_page(__name__)

def layout():
    if current_user.is_authenticated == True:
        logout_user()

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
                                            html.Div(html.H3("You have been logged out - Please login")),
                                            html.Br(),
                                            dbc.Button("Login", href="/login"),
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