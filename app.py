import calendar
from datetime import date, timedelta
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
from SPAPI.amzService import AmzService
from SPAPI.salesService import SalesService
from SPAPI.inventoryService import InventoryService
from SPAPI.catalogService import CatalogService
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames
from credentials import credentials
from flask import Flask, session
import tkinter as tk
import math
from utils.functions import create_card
import json
import json

salesService = SalesService()
inventoryService = InventoryService()


def show_averages():
    print('Getting sales and 8 week averages...')
    row = []
    row.append(html.H2("Sales Last Week"))
    last_week = date.today() - timedelta(weeks=1)
    last_start = last_week - timedelta(days=last_week.weekday())
    eight_weeks = last_week - timedelta(weeks=8)
    eight_start = eight_weeks - timedelta(days=eight_weeks.weekday())

    for asin in asinSkuMapper.keys():
        df_last = salesService.getSalesByDay(asin, last_start, last_start + timedelta(days=6))
        df_eight = salesService.getSalesByDay(asin, eight_start, eight_start + timedelta(days=56))

        df = pd.DataFrame({"ASIN": [asin], "Product": [asinNames.get(asin)], "Sales Last Week": [df_last['Sales'].sum()], "Sales Avg": [df_eight['Sales'].sum() / 8]})

        sales_lw = float(format(df.get('Sales Last Week')[0], '.2f'))
        sales_avg = float(format(df.get('Sales Avg')[0], '.2f'))
        decorator = ''
        if(sales_lw >= sales_avg):
            decorator = 'bg-success text-white'
        else:
            decorator = 'bg-warning text-dark'


        col = dbc.Col([
            html.Div([
                html.Div([
                    html.P(df.get('Product')[0], className='card-title'),
                    html.Div('$' + str(sales_lw), style={'font-weight': 'bold'}),
                    html.Div('$' + str(sales_avg), style={'opacity':'.8'})], className="card-body")], className='card ' + decorator)
                ], className='col-lg-3', style={'padding':'3px'})
        row.append(col)
    return row



# ===================== TODAY'S SALES ==============================
def getSalesForToday():
    amzService = AmzService()
    df = amzService.getSales('', date.today(), date.today(), 'Day')
    df.columns = ['Day', 'Unit Count', 'Order Item Count', 'Order Count', 'Avg Unit Price', 'Currency', 'Total Sales', 'Currency2']
    print(df)
    
    bg_color = int(round(df.get('Total Sales')[0], -2))
    
    return dbc.Row(
        [
            dbc.Col(create_card('Sales', 'sales-card', 'fa-sack-dollar', str('${:,.2f}'.format(df.get('Total Sales')[0]))), width=4,),
            dbc.Col(create_card('Units', 'units-card', 'fa-tag', df.get('Unit Count')[0]), width=4,),
            dbc.Col(create_card('Orders', 'orders-card', 'fa-bag-shopping', df.get('Order Count')[0]), width=4,),
        ]
    )



# ===================== SALES BY ASIN BY DATE RANGE ==============================
def getSalesForDatePicker(start, end, asin, granularity):
    df = salesService.getSalesForDatesByAsin(start, end, asin, granularity)
            
    if granularity == 'Week':
        df = df.groupby(['Week', 'ASIN', 'Product'], sort=False, observed=True)['Sales'].sum().reset_index()
    elif granularity == 'Month':
        df = df.groupby(['Month', 'ASIN', 'Product'], sort=False, observed=True)['Sales'].sum().reset_index()
        df['Month'] = pd.Categorical(df['Month'], categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], ordered=True)
        df.sort_values(by='Month', inplace=True)
    else:
        # Change from Day to Date for bar chart
        granularity = 'Date'
    
    bar_chart = px.bar(df, x=granularity, y="Sales", color="Product", barmode="stack", template="minty")
    bar_chart.layout.xaxis.fixedrange = True
    bar_chart.layout.yaxis.fixedrange = True
    bar_chart.update_layout(showlegend = False)
    pie_chart = px.pie(df, values='Sales', names='Product', template="minty")
    pie_chart.update_layout(showlegend = False)

    return html.Div([
            html.Div(dcc.Graph(figure = bar_chart), className='col-lg-8'),
            html.Div(dcc.Graph(figure = pie_chart), className='col-lg-4')
        ], className='row')






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
        lgis.append(dbc.ListGroupItem(str(r[1]['Ranking']) + " " + r[1]['ASIN']))
    
    list_group = dbc.ListGroup(lgis, flush=True,)
    
    return dbc.Row(
        [
            dbc.Col(grid),
            dbc.Col(create_card('Organic Search Ranking', 'ranking-card', 'fa-medal', list_group), width=4,)
        ]
    )





# ===================== Initialize the app ==============================
load_figure_template("minty")
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    credentials['VALID_USERNAME_PASSWORD_PAIR'],
    secret_key = credentials['DASH_SECRET_KEY']
)

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
    
# ===================== Run the app ==============================
if __name__ == '__main__':
    app.run(debug=True)

