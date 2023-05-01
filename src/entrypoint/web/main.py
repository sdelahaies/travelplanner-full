from os import environ

import dash
from dash import dcc, html, Input, Output, State
from flask import Flask
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask import jsonify, request, redirect

from src.interface.search import Search
from src.interface.user import User as UserInterface
from src.interface.user_point_of_interest_history import UserPointOfInterestHistory
from src.entrypoint.web.pages.utils import *

server = Flask(__name__)

server.config['APP_NAME'] = environ.get("APP_NAME")
server.config['FLASK_ENV'] = environ.get("FLASK_ENV")
server.config['DEBUG'] = environ.get("FLASK_DEBUG")
server.config['SECRET_KEY'] = environ.get("SECRET_KEY")

app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY]#[dbc.themes.DARKLY]
)

app.title = "Travel Planner"

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username, id):
        self.id = username
        self.user_id = id
        if username == "sylvain":
            self.role = "admin"
        else:
            self.role = "user"

@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    user = UserInterface(username=username, password=None)
    response = user.find()
    return User(username, id=response.get("_id"))

links = dbc.Row(
    [
        dbc.Col(dbc.NavLink("Home", href="/",style={"color": "#ccc1c1"})),
        dbc.Col(dbc.NavLink("Planner", href="/planner",style={"color": "#ccc1c1", 'margin-left': '10px'})),
        dbc.Col(dbc.NavLink("Auto-Planner", href="/autoplanner",style={"color": "#ccc1c1", 'margin-left': '10px', "width": "100px"})),
        dbc.Col(dbc.NavLink("Planner History", href="/history",style={"color": "#ccc1c1", 'margin-left': '10px', "width": "115px"})),
        dbc.Col(dbc.NavLink("About", href="/about",style={"color": "#ccc1c1", 'margin-left': '10px'})),
        dbc.Col(dbc.NavLink(id="user-status-header", href="/", style={"color": "#ccc1c1"}), width={"size": 8}, style={'margin-left': '10px'}),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    justify="right",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src="assets/poi_w.png", height="30px")),
                        dbc.Col(dbc.NavbarBrand(
                            "Travel Planner", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"}
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                links,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    sticky='top',
    className="flex-md-row"
)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dash.page_container,
    ]
)


@app.callback(
    Output("user-status-header", "children"),
    Input("url", "pathname"),
)
def update_authentication_status(_):
    if current_user.is_authenticated == True:
        return dbc.NavLink("Logout", href="/logout")

    return dbc.NavLink("Login", href="/login")


@app.callback(
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        user = UserInterface(username, password)

        if user.find() is None:
            return dbc.Alert("Invalid username", color="danger"),

        if user.verify_password():
            current_user = user.find()
            login_user(User(username=current_user.get("username"), id=current_user.get("_id")))
            return dbc.Alert("Login Successful", color="primary"),

        return dbc.Alert("Incorrect password username", color="danger"),

@server.route("/api/poi", methods=['GET'])
@login_required
def api_poi():
    
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    print('-----------------------------------------------')
    print('test 2:',longitude,latitude)
    kinds = str_to_list(request.args.get('kinds'))
    limit = request.args.get('limit')
    radius = request.args.get('radius')
    result = Search(latitude=latitude, longitude=longitude, kinds=kinds,limit=limit,radius=radius).launch()
    return jsonify({"response": result})

@server.route("/api/poi/history", methods=['POST'])
@login_required
def api_poi_history():
    pois = request.json
    point_of_interest_lists = pois.get("pois", [])

    for item in point_of_interest_lists:
        history = UserPointOfInterestHistory(user_id=current_user.user_id, point_of_interest_id=item["id"], rating=item["rating"])
        history.create()

    return jsonify()

@server.route("/api/poi/history", methods=['GET'])
@login_required
def api_poi_get_history():
    history = UserPointOfInterestHistory(user_id=current_user.user_id)
    result = history.find_by_user_id()

    return jsonify({"response": result})

if __name__ == "__main__":
    app.run_server()
