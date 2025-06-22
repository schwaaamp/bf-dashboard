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



load_dotenv()  # loads variables from .env into environment



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
    logging.info('Getting inventory...')
    inventoryService = InventoryService()
    inventoryDf = inventoryService.getInventoryNeeds()
    logging.info('Inventory service results:')
    logging.info(inventoryDf)
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
    
    logging.info('Returning the updated dataframe...')
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
