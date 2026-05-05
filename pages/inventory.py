import dash
from dash import callback, dcc, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from inventoryService import InventoryService
#import anthropic
from dotenv import load_dotenv
import os
import logging
import warnings



load_dotenv()  # loads variables from .env into environment
warnings.filterwarnings("ignore")


dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/inventory",
)

# ===================== Get Inventory ==============================
def get_inventory_component(inventoryDf):
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
        { 'field': 'Weeks Incl. Inbound', "type": "numericColumn"},
    ]

    logging.info('Setting the AgGrid with updated dataframe...')
    grid = dag.AgGrid(
        id="inventoryNeeds",
        rowData=inventoryDf.to_dict("records"),
        columnDefs=columnDefs,
        columnSize="sizeToFit",
        dashGridOptions={"domLayout": "autoHeight"},
        style={"width": "400px"}
    )
    
    
    # start anthropic
    #client = anthropic.Anthropic(
    #    api_key=os.getenv('bf_dashboard_anthropic_key')
    #)
    #message = client.messages.create(
    #    model="claude-3-5-haiku-20241022",
    #    max_tokens=1024,
    #    messages=[
    #        {"role": "user", "content": "Hello, Claude"}
    #    ]
    #)
    #print(message.content)
    # end anthropic
    
    return dbc.Col(grid, className='col-sm')




# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2("Inventory", className="title"),
                html.Br(),
                dcc.Interval(id="refresh-inventory", interval=100, n_intervals=0, max_intervals=1),
                html.Div(id="inventory-output"),
                html.Br(),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)


# Callback
@callback(Output("inventory-output", "children"), Input("refresh-inventory", "n_intervals"))
def update_inventory(n):
    inventoryService = InventoryService()
    inventoryDf = inventoryService.getInventoryNeeds()
    logging.info(inventoryDf)
    return get_inventory_component(inventoryDf)