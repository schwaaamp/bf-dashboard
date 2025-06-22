import dash
from dash import callback, dcc, html, Input, Output
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames
from catalogService import CatalogService
import warnings

warnings.filterwarnings("ignore")

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/competition",
)

# ===================== Show organic search results for terms ==============================
def get_competition_component(df_list):
    columnDefs = [
        #{ 'field': 'ASIN'},
        { 'field': 'Ranking', 'headerName':'#'},
        { 'field': 'Brand'},
        { 'field': 'Listing Price', "valueFormatter": {"function": "'$' + (params.value ? params.value : 0)"},},
        { 'field': 'Category Rank'},
        { 'field': 'Link', 'headerName':'Listing', "linkTarget":"_blank"},
    ]

    # for each df, create a div of results and append to row
    df_col = []
    
    for df in df_list:
        children = []
        wrapperDiv = []
        grid = dag.AgGrid(
            id="organicSearch",
            rowData=df.to_dict("records"),
            columnDefs=columnDefs,
            columnSize="autoSize",
            defaultColDef={"cellRenderer": "markdown"},
        )
        
        wrapperDiv = html.Div([html.H3(df['Query'].values[0]), html.Div(grid)], className='col-lg-6')
        df_col.append(wrapperDiv)
        
    searchRow = dbc.Row(df_col)
        

    '''
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
    '''
    #return dbc.Row([dbc.Col(grid), dbc.Col(create_card('Organic Search Ranking', 'ranking-card', 'fa-medal', list_group), ),]), searchRow
    return searchRow


# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Competition",  # title
                    className="title",
                ),
                html.Br(),
                dcc.Interval(id="refresh-competition", interval=100, n_intervals=0, max_intervals=1),
                html.Div(id="competition-output"),
                html.Br(),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)

# Callback
@callback(Output("competition-output", "children"), Input("refresh-competition", "n_intervals"))
def update_competition(n):
    catalogService = CatalogService()
    df_list = catalogService.getSearchResults()
    return get_competition_component(df_list)