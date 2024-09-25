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

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/competition",
)

import warnings

warnings.filterwarnings("ignore")

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
                showOrganicSearch(),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            create_card("Purchases", "purchases-card", "fa-list", "Chilfdren"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Total Spend", "spend-card", "fa-coins", "Chilfdren"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Top Category", "category-card", "fa-tags", "Chilfdren"),
                            width=4,
                        ),
                    ],
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="sales-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "400px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="category-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "400px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                    ],
                ),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)

