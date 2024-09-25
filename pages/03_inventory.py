import dash
from dash import callback, dcc, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from inventoryService import InventoryService

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/inventory",
)

import warnings

warnings.filterwarnings("ignore")

# ===================== Get Inventory ==============================
def getInventory():
    inventoryService = InventoryService()
    df = inventoryService.getInventoryNeeds()    
    columnDefs = [
        { 'field': 'ASIN'},
        { 'field': 'Available', "type": "numericColumn"},
        { 'field': 'Total On Hand', "type": "numericColumn"},
        { 'field': 'Weeks On Hand', 
            "type": "numericColumn",
            'cellClassRules': {
                'bg-danger text-white font-weight-bold': '6 > params.value',
            },
        },
    ]

    grid = dag.AgGrid(
        id="inventoryNeeds",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        columnSize="sizeToFit",
        style={"height": "344px", "width": "400px"}
    )
    return dbc.Col(grid, className='col-sm')




# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Inventory",  # title
                    className="title",
                ),
                html.Br(),
                dbc.Row([
                    getInventory(),
                ]),
                html.Br(),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)
