import dash
from dash import callback, dcc, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames
from catalogService import CatalogService
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


# ===================== Show organic search results for terms ==============================
def showOrganicSearch():
    catalogService = CatalogService()
    df = catalogService.getSearchResults()
      
    columnDefs = [
        { 'field': 'ASIN'},
        { 'field': 'Brand'},
        { 'field': 'Item Name'},
    ]
    
    grid = dag.AgGrid(
        id="organicSearch",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        columnSize="autoSize",
    )
    
    rankings = pd.DataFrame(columns=['ASIN', 'Ranking'])
    
    for asin in asinSkuMapper.keys():
        rankings = pd.concat([rankings, df.loc[df['ASIN'] == asin]])
        
    lgis = []
    for r in rankings.iterrows():
        decorator = ''
        if r[1]['Ranking'] == 1:
            decorator = 'list-group-item-success'
        else:
            decorator = 'list-group-item-danger'
        lgis.append(dbc.ListGroupItem(str(r[1]['Ranking']) + "      " + asinNames.get(r[1]['ASIN']), class_name=decorator))
    
    list_group = dbc.ListGroup(lgis, flush=True,)
    
    return dbc.Row(
        [
            dbc.Col(grid),
            dbc.Col(create_card('Organic Search Ranking', 'ranking-card', 'fa-medal', list_group), width=4,)
        ]
    )


# Add all as an option in the ASIN dropdown
asinDD = asinSkuMapper.copy()
asinDD["All"] = ["All", "All"]

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
                html.H2("This doesn't belong here"),
                showOrganicSearch(),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)
