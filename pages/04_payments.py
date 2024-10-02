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
    
    return dbc.Row(
        [
            dbc.Col(create_card(df.get('Currency')[0], 'currency-card', 'fa-sack-dollar', df.get('Total Balance')[0]), style={'padding':'3px'}),
            #dbc.Col(create_card('Units', 'units-card', 'fa-tag', df.get('Unit Count')[0]), style={'padding':'3px'}),
            #dbc.Col(create_card('Orders', 'orders-card', 'fa-bag-shopping', df.get('Order Count')[0]), style={'padding':'3px'}),
        ]
    )

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
                getOpenPayments(),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)