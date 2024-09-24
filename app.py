import calendar
from datetime import date, timedelta
import dash
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
#from pages.inventoryService import InventoryService
#from pages.catalogService import CatalogService
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames
from credentials import credentials
from flask import Flask, session
import tkinter as tk
import math
from utils.functions import create_card

#inventoryService = InventoryService()





'''
# ===================== Get Inventory ==============================
def getInventory():
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
'''




# ===================== Initialize the app ==============================
load_figure_template("minty")
app = Dash(
    __name__, 
    use_pages=True,
    title="Amazon Dashbaord",
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME], 
    suppress_callback_exceptions=True
)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    credentials['VALID_USERNAME_PASSWORD_PAIR'],
    secret_key = credentials['DASH_SECRET_KEY']
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
                    "Sales", href="/sales", active="exact"
                ),
                dbc.NavLink(
                    "Competition",
                    href="/competition",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Span("Created by "),
                html.A(
                    "Mayara Daher",
                    href="https://github.com/mayaradaher",
                    target="_blank",
                ),
                html.Br(),
                html.Span("Data Source "),
                html.A(
                    "MIT Publication",
                    href="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YGLYDY",
                    target="_blank",
                ),
            ],
            className="subtitle-sidebar",
            style={"position": "absolute", "bottom": "10px", "width": "100%"},
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
        content,
        dash.page_container,
    ]
)


# ================================= ALL MY OLD STUFF =================================
'''
# Add all as an option in the ASIN dropdown
asinDD = asinSkuMapper.copy()
asinDD["All"] = ["All", "All"]

app.layout = html.H1(children='Amazon Sales'), html.Div([
    getSalesForToday(),
        dbc.Row([
            html.Div(dbc.Row(show_averages()), className='col-sm'), 
            html.Div([html.H2('Inventory needs'), getInventory()], className='col-sm')], className='my-1'),
            dbc.Row(dbc.Col(html.H2('Product Sales'))),
            dbc.Row([
                dbc.Col([
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        initial_visible_month=date.today(),
                        start_date=date.today() - timedelta(days=30),
                        end_date=date.today()
                    )], width="auto"),
                dbc.Col([dcc.Dropdown(list(asinDD.keys()), 'All', id='asin-dd', clearable=False, style={'width':'130px'})], width="auto"),
                dbc.Col([dcc.Dropdown(['Day', 'Week', 'Month'], 'Week', id='granularity-dd', clearable=False, style={'width':'100px'})], width="auto")], className='my-1'),
            dbc.Row([dbc.Col(html.Div(id='sales-report-body'))]),
            showOrganicSearch(),
            html.P('https://sellercentral.amazon.com/sp-api-status')], 
        className='container')


@callback(
    Output('sales-report-body', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('asin-dd', 'value'),
    Input('granularity-dd', 'value'))
def update_output(start_date, end_date, asin, granularity):
    if start_date is not None and end_date is not None:
        return getSalesForDatePicker(start_date, end_date, asin, granularity)
    else:
        return ''
'''
    
# ===================== Run the app ==============================
if __name__ == '__main__':
    app.run(debug=True)

