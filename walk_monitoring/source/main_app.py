import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
person_ids = [1, 2, 3, 4, 5, 6]


def main():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H4(id='header', children='Nasz Header'),
        html.Button('Id 1', id='button1'),
        html.Button('Id 2', id='button2'),
        html.Button('Id 3', id='button3'),
        html.Button('Id 4', id='button4'),
        html.Button('Id 5', id='button5'),
        html.Button('Id 6', id='button6'),
        html.Div(id='content', children=''),
        dcc.Interval(
            id='clock',
            interval=1000,
            n_intervals=0
        )
    ])

    @app.callback(
        [Output('content', 'children')],
        [Input('clock', 'n_intervals'),
         Input('button1', 'n_clicks_timestamp'),
         Input('button2', 'n_clicks_timestamp'),
         Input('button3', 'n_clicks_timestamp'),
         Input('button4', 'n_clicks_timestamp'),
         Input('button5', 'n_clicks_timestamp'),
         Input('button6', 'n_clicks_timestamp'),
         ]

    )
    def tick(n_intervals, t1, t2, t3, t4, t5, t6):
        buttons_times = [t1, t2, t3, t4, t5, t6]
        for i, time in enumerate(buttons_times):
            buttons_times[i] = 0 if time is None else time
        max_val = max(buttons_times)
        current_id = buttons_times.index(max_val) + 1
        url = f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{current_id}'
        json_data = json.loads(requests.get(url).text)
        print(n_intervals)
        sensors = json_data['trace']['sensors']
        sensor_paragraphs = [html.P(f'id: {s["id"]}, value: {s["value"]} anomaly: {s["anomaly"]}, ') for s in sensors]
        return [html.Div([
            html.H1('Name:'),
            html.P(f"{json_data['firstname']} {json_data['lastname']}"),
            *sensor_paragraphs
        ])]

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
