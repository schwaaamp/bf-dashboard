import dash_bootstrap_components as dbc
from dash import html
from asinSkuUtil import asinSkuMapper


def create_card(title, card_id, icon_class, children):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(
                            className=f"fa-solid {icon_class} card-icon",
                        ),
                        html.H3(title, className="card-title"),
                    ],
                    className="d-flex align-items-center",
                ),
                html.H4(id=card_id, children=children),
            ],
            className="card-body",
        ),
        className="card",
    )
    
def getSkuForAsin(self, asin):
    sku = asinSkuMapper.get(asin)[0]
    return sku
    
# I think this will only be needed for test cases
def getAsinForSku(self, sku):
    asin = list(asinSkuMapper.keys())[list(asinSkuMapper.values()).index(sku)]
    return asin