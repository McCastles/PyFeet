import json
import os
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import requests
from dash.dependencies import Input, Output, State
from flask_caching import Cache
import uuid
from DashDBmanager import DashDBmanager
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import json
import requests
import numpy as np
import base64

external_stylesheets = [dbc.themes.BOOTSTRAP]

person_ids = [1, 2, 3, 4, 5, 6]
x_range = 100
n_traces = 6
left_trace_range = range(3)
right_trace_range = range(3, 6)
feet_img = base64.b64encode(open('feet.png', 'rb').read())

ticklabels = True

db_path = '../../walktraceDB.db'

# db_instance = DashDBmanager(db_path)

db_managers = {}


def prepare_array(series, value):
    if len(series) < x_range:
        arr = np.zeros(x_range)
        np.put(arr, np.arange(len(series)), series)
        series = arr  # .tolist()
    else:
        series = series[1:]
        series.append(value)
    return series


def create_figure_for_trace(traces, current_range, title):
    xticks = np.arange(x_range)
    return {
        'data': [{
            'x': xticks,
            'y': series,
            'name': f'sensor{list(current_range)[i] + 1}',
            'text': f'sensor{list(current_range)[i] + 1}'
        } for i, series in enumerate(traces)],
        'layout': {
            'title': title,
            'yaxis': {
                'title': 'sensor value'
            },
            'height': 300
        }
    }


def get_color(value, anomaly):
    r = g = b = 0
    if anomaly:
        r = min(int(90 + value * 110 / 1023), 255)
    else:
        g = min(int(90 + value * 110 / 1023), 255)
    return f'rgb({r}, {g}, {b})'


def create_figure_for_feet(sensors_data):
    sensor_values = [s['value'] for s in sensors_data]
    colors = [get_color(s['value'], s['anomaly']) for s in sensors_data]

    fig = go.Figure(
        layout=go.Layout(images=[{
            'source': f'data:image/png;base64, {feet_img.decode()}',
            'xref': 'x',
            'yref': 'y',
            'x': 0,
            'y': 1,
            'sizex': 1,
            'sizey': 1,
            'sizing': 'stretch',
            'layer': 'below',

        }
        ],
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': ticklabels, 'range': [0, 1]},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': ticklabels, 'range': [0, 1]},
            height=600,
            width=600

        ))
    fig.add_annotation(
        go.layout.Annotation(x=0.36, y=0.7, text='sensor 1', arrowhead=7, ax=45, ay=0, arrowcolor="grey"))
    fig.add_annotation(
        go.layout.Annotation(x=0.22, y=0.6, text='sensor 2', arrowhead=7, ax=45, ay=40, arrowcolor="grey"))
    fig.add_annotation(
        go.layout.Annotation(x=0.24, y=0.2, text='sensor 3', arrowhead=7, ax=-45, ay=0, arrowcolor="grey"))
    fig.add_annotation(
        go.layout.Annotation(x=0.65, y=0.7, text='sensor 4', arrowhead=7, ax=-45, ay=20, arrowcolor="grey"))
    fig.add_annotation(
        go.layout.Annotation(x=0.83, y=0.6, text='sensor 5', arrowhead=7, ax=-75, ay=40, arrowcolor="grey"))
    fig.add_annotation(
        go.layout.Annotation(x=0.74, y=0.2, text='sensor 6', arrowhead=7, ax=65, ay=0, arrowcolor="grey"))
    fig.add_trace(go.Scatter(x=[0.3, 0.16, 0.3, 0.7, 0.86, 0.7], y=[0.7, 0.6, 0.2, 0.7, 0.6, 0.2], mode='markers+text',
                             marker={'size': 36, 'color': colors}, text=sensor_values,
                             textfont={'color': 'white', 'size': 18}))
    return fig


def build_data_storage_dict():
    store = {
        'patient_id': 1,
        'uuid': None
    }

    for i in range(n_traces):
        store[f'trace{i}'] = []
    print(store)
    return store


def main():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H4(id='header', children='Nasz Header'),
        html.Div(id='changed', children=''),
        *[html.Button(f'Id {i}', id=f'button{i}') for i in range(1, 7)],
        html.Div(id='content', children=''),
        dcc.Interval(
            id='clock',
            interval=500,
            n_intervals=0
        ),
        dcc.Store('current_patient_id_input', data=build_data_storage_dict()),
        dcc.Store('current_patient_id_output', data=build_data_storage_dict()),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(
                        id='trace_left',
                        figure={
                            'data': [{
                                'x': np.arange(x_range),
                                'name': 'Trace'
                            }]
                        }
                    ),
                        dcc.Graph(
                            id='trace_right',
                            figure={
                                'data': [{
                                    'x': np.arange(x_range),
                                    'name': 'Trace'
                                }]
                            }
                        )
                    ], width=9),
                dbc.Col(
                    dcc.Graph(
                        id='feet',
                        # figure=create_figure_for_feet()
                    ), width=3)
            ])
    ])

    @app.callback(
        [Output('content', 'children'),
         Output('current_patient_id_output', 'data'),
         Output('changed', 'children'),
         Output('trace_left', 'figure'),
         Output('trace_right', 'figure'),
         Output('feet', 'figure')],
        [Input('clock', 'n_intervals'),
         *[Input(f'button{i}', 'n_clicks_timestamp') for i in range(1, 7)],
         ],
        [State('current_patient_id_input', 'data')]

    )
    def tick(_, t1, t2, t3, t4, t5, t6, data):
        if not data['uuid']:
            uid = str(uuid.uuid4())
            while uid in db_managers:
                uid = str(uuid.uuid4())
            data['uuid'] = uid
            db_managers[uid] = DashDBmanager(db_path)
        db_manager = db_managers[data['uuid']]

        print(db_manager)
        
 

        buttons_times = [t1, t2, t3, t4, t5, t6]
        for i, time in enumerate(buttons_times):
            buttons_times[i] = 0 if time is None else time
        max_val = max(buttons_times)
        patient_id = buttons_times.index(max_val) + 1

        changed = patient_id != data['patient_id']

        if changed:
            data['patient_id'] = patient_id
            for i in range(n_traces):
                data[f'trace{i}'] = []

        # url = f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{patient_id}'
        url = f'http://127.0.0.1:5000/{patient_id}'
        json_data = json.loads(requests.get(url).text)
        sensors = json_data['trace']['sensors']
        sensor_paragraphs = [html.P(f'id: {s["id"]}, value: {s["value"]} anomaly: {s["anomaly"]}, ') for s in sensors]
        


        row = DashDBmanager.parseJSON(json_data)
  
        db_manager.insert_row(row)
        
        db_manager.select_all()


        for i in range(n_traces):
            series = prepare_array(data[f'trace{i}'], sensors[i]['value'])
            data[f'trace{i}'] = series
        fig_left = create_figure_for_trace([data[f'trace{i}'] for i in left_trace_range], left_trace_range,
                                           'Left Foot Sensors Trace')
        fig_right = create_figure_for_trace([data[f'trace{i}'] for i in right_trace_range], right_trace_range,
                                            'Right Foot Sensors Trace')
        fig_feet = create_figure_for_feet(sensors)

        return html.Div([
            html.H1('Name:'),
            html.P(f"{json_data['firstname']} {json_data['lastname']}"),
            *sensor_paragraphs
        ]), data, html.H1(str(changed)), fig_left, fig_right, fig_feet

    @app.callback(
        Output('current_patient_id_input', 'data'),
        [Input('current_patient_id_output', 'data')]
    )
    def store_current_patient_id(data):
        return data

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
