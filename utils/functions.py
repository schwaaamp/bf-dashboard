import dash_bootstrap_components as dbc
from dash import html


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
                html.H4(children=children),
            ],
            className="card-body",
        ),
        className="card",
        id=card_id,
    )