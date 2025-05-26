import dash
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dotenv import load_dotenv
import os
import json
from flask import Flask, session



load_dotenv()  # loads variables from .env into environment



# ===================== Initialize the app ==============================
load_figure_template("minty")
valid_pairs_str = os.getenv('VALID_USERNAME_PASSWORD_PAIR')
valid_pairs = json.loads(valid_pairs_str)  # parse string into dict

app = Dash(
    __name__, 
    use_pages=True,
    title="Amazon Dashboard",
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME], 
    suppress_callback_exceptions=True
)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    valid_pairs,
    secret_key = os.getenv('DASH_SECRET_KEY')
)

# sidebar
sidebar = html.Div(
    [
        dbc.Row(
            [html.Img(src="assets/logos/bf_logo.png", style={"height": "70px"})],
            className="sidebar-logo",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Sales", href="/sales", active="exact", className='nav-sales'
                ),
                dbc.NavLink(
                    "Competition",
                    href="/competition",
                    active="exact",
                ),
                dbc.NavLink(
                    "Inventory", href="/inventory", active="exact"
                ),
                dbc.NavLink(
                    "Payments", href="/payments", active="exact"
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

content = html.Div(
    className="page-content",
)


# layout
app.layout = html.Div(
    [
        dcc.Location(id="url", pathname="/sales"),
        sidebar,
        #content,
        dash.page_container,
    ]
)
    
# ===================== Run the app ==============================
if __name__ == '__main__':
    app.run(debug=True)

