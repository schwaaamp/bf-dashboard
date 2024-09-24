import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/competition",
)

import warnings

warnings.filterwarnings("ignore")


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
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "Select Year",
                                    className="subtitle-small",
                                )
                            ],
                            width=4,
                        ),
                    ]
                ),
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

