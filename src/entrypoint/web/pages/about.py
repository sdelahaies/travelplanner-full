import dash
from dash import html, dcc
from flask_login import current_user
import dash_bootstrap_components as dbc

dash.register_page(__name__)

def layout():
    if current_user.is_authenticated == False:
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
                                            html.Div([
                                                html.H3("About"),
                                                html.H4("Projet fil rouge formation Data Engineer @ DataScientest, jan2023 Bootcamp"), 
                                                html.H4("A. Bouttier, S. Delahaies, H. Elmi Ali, I. Noui"),
                                                html.P("Itinéraire de vacance: conception, implémentation, déploiement d’une application permettant de proposer un itinéraire de vacance selon certains critères."),
                                                html.P("L’utilisateur de l’application choisit des zones / points d’intérêt (POI) à visiter lors de son prochain voyage, ainsi que la durée du séjour et ses centres d'intérêts, l’app lui propose un itinéraire détaillé produit à partir d'un système de recommandation ou laisse la possibilité de constituer lui même un panier d'activité.")
                                                    ]
                                                ),
                                            
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