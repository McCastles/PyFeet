import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import requests


def main():
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.H4(id='header', children='Nasz Header'),
        html.Div(id='content', children='')
    ])

    @app.callback(
        [Output('content', 'children')]
    )
    def say_hello():
        return [html.Div(children='Hello!')]

    app.run_server(debug=True)

    print('added for testing')


if __name__ == '__main__':
    main()
