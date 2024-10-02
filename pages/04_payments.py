import dash
from dash import callback, dcc, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from financialEventsService import FinancialEventsService

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/payments",
)

import warnings

warnings.filterwarnings("ignore")

# ===================== Get Inventory ==============================
def getOpenPayments():
    financialEventsService = FinancialEventsService()
    df = financialEventsService.getOpenPayments()
    
    dbcRow = []
    
    for index, row in df.iterrows():
        col = dbc.Col(create_card(row.get('Currency'), 'currency-card', 'fa-sack-dollar', row.get('Total Balance')), style={'padding':'3px'})
        dbcRow.append(col)
    
    return dbcRow

# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Open Payments",  # title
                    className="title",
                ),
                html.Br(),
                dbc.Row(getOpenPayments()),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)