# Import packages
import calendar
from datetime import date, timedelta
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
from amzService import AmzService
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames
from credentials import credentials
from salesService import SalesService
from inventoryService import InventoryService
from flask import Flask, session

salesService = SalesService()
inventoryService = InventoryService()
cols_clean =['Day', 'Unit Count', 'Order Item Count', 'Order Count', 'Avg Unit Price', 'Currency', 'Total Sales', 'Currency2']


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


        col = html.Div([
            html.Div([
                html.Div([
                    html.P(df.get('Product')[0], className='card-title'),
                    html.Div('$' + str(sales_lw), style={'font-weight': 'bold'}),
                    html.Div('$' + str(sales_avg), style={'opacity':'.8'})], className="card-body")], className='card ' + decorator)
                ], id=asin, className="col-sm-3 card-custom")
        row.append(col)
    return row



# ===================== TODAY'S SALES ==============================
# Separate function from sales by asin because this should not be cached
def getSalesForToday():
    amzService = AmzService()
    df = amzService.getSales('', date.today(), date.today(), 'Day')
    df.columns = cols_clean

    return html.H2('Today\'s Sales (US)'), html.Div([
            html.Div([
                html.Div([
                    html.H5(str('${:,.2f}'.format(df.get('Total Sales')[0]))),
                    html.P(str(df.get('Unit Count')[0]) + ' units'),
                    html.P(str(df.get('Order Count')[0]) + ' orders')
                ])
            ], className='card-body')], 
        className='card', style={'text-align':'center'})



# ===================== SALES BY ASIN BY DATE RANGE ==============================
def getSalesForDatesByAsin(start, end, asin, granularity):
    print('Getting sales for date picker...')
    start = date.fromisoformat(start)
    end = date.fromisoformat(end)
    df = pd.DataFrame()
    if asin != 'All':
        df = salesService.getSales(asin, start, end, granularity)
        df['ASIN'] = asin
        df['Product'] = asinNames.get(asin)
    else:
        for asin in asinSkuMapper.keys():
            tempDf = salesService.getSales(asin, start, end, granularity)
            tempDf['ASIN'] = asin
            tempDf['Product'] = asinNames.get(asin)
            df = pd.concat([df, tempDf])

    if granularity == 'Week':
        df = df.groupby(['Week', 'ASIN', 'Product'], observed=True)['Sales'].sum().reset_index()
    elif granularity == 'Month':
        df = df.groupby(['Month', 'ASIN', 'Product'], observed=True)['Sales'].sum().reset_index()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        df['Month'] = pd.Categorical(df['Month'], categories=months, ordered=True)
        df.sort_values(by='Month', inplace=True)
    else:
        # Change from Day to Date for bar chart
        granularity = 'Date'

    bar_chart = px.bar(df, x=granularity, y="Sales", color="Product", barmode="stack", template="minty")
    bar_chart.layout.xaxis.fixedrange = True
    bar_chart.layout.yaxis.fixedrange = True
    pie_chart = px.pie(df, values='Sales', names='Product', title='Sales by Product', template="minty")
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
        { 'field': 'Available', "type": "numericColumn" },
        { 'field': 'Total On Hand', "type": "numericColumn" },
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
        columnSize="responsiveSizeToFit",
    )
    return grid





# ===================== Initialize the app ==============================
load_figure_template("minty")
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)
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
        html.Div([
            html.Div([html.Div(show_averages(), className='row')], className='col-lg-5'), 
            html.Div(getSalesForToday(), id='todays-sales', className='col-lg-3'),
            html.Div([html.H2('Inventory needs'), getInventory()], className='col-lg-4')], className='row'),
            html.Div([
                html.Div([
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        initial_visible_month=date.today(),
                        start_date=date.today() - timedelta(days=30),
                        end_date=date.today()
                    )], className='col-3'),
                html.Div([
                    dcc.Dropdown(list(asinDD.keys()), 'All', id='asin-dd')], className='col-3'),
                html.Div([dcc.Dropdown(['Day', 'Week', 'Month'], 'Day', id='granularity-dd')], className='col-3')], className='row justify-content-start'),
            html.Div(id='sales-report-body'),
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
        return getSalesForDatesByAsin(start_date, end_date, asin, granularity)
    else:
        return ''
    
# ===================== Run the app ==============================
if __name__ == '__main__':
    app.run(debug=True)

