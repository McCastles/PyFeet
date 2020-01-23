import dash
import dash_core_components as dcc
import dash_html_components as html
import uuid
from DashDBmanager import DashDBmanager
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import json
import requests
import numpy as np
import pandas as pd
import base64
import dash_table

external_stylesheets = [dbc.themes.BOOTSTRAP]

df = pd.DataFrame([{'a': 1, 'b': 2, 'c': 3} for i in range(100)])
print(df.columns)

columns=[{"name": i, "id": i} for i in df.columns]
data=df.to_dict('rows')

print(f"columns: {columns}")
print(f'data: {data}')

x_range = 600
n_traces = 6
n_patients = 6
left_trace_range = range(3)
right_trace_range = range(3, 6)
feet_img = base64.b64encode(open('feet.png', 'rb').read())
tick_time = 500
pause_time = 60 * 60 * 1000

db_path = '../../walktraceDB.db'

db_managers = {}


def prepare_and_rotate_array(series, value):
    if len(series) < x_range:
        arr = np.zeros(x_range)
        np.put(arr, np.arange(len(series)), series)
        series = arr
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
            'text': f'sensor{list(current_range)[i] + 1}',
        } for i, series in enumerate(traces)],
        'layout': {
            'title': {'text': title,
                      'font': dict(
                          size=30,
                      ),
                      },

            'yaxis': {
                'title': {'text': 'sensor value', 'fontsize': 20},
                'gridcolor': '#808080',
                # 'tick0': 0,
                # 'dtick': 200,
                'type': "log"
            },
            'xaxis': {'color': 'white', 'tickmode': 'array', 'tickvals': np.arange(0, 600, 100),
                      'ticktext': np.arange(600, 0, -100)},
            'height': 300,
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
            'font': {'family': 'Courier New, monospace', 'color': 'white', 'size': 15}
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
    sensor_font = dict(
        size=20,
        color="#d1c3c0"
    )
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
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False, 'range': [0, 1]},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False, 'range': [0, 1]},
            height=600,
            width=600,
            plot_bgcolor='black',
            paper_bgcolor='black',
            title={
                'text': "sensor values visualization",
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(
                    family="Courier New, monospace",
                    size=30,
                    color="#7f7f7f"
                )
            },

        ))
    fig.add_annotation(
        go.layout.Annotation(x=0.36, y=0.7, text='S1', arrowhead=7, ax=45, ay=0, arrowcolor="grey", font=sensor_font))
    fig.add_annotation(
        go.layout.Annotation(x=0.22, y=0.6, text='S2', arrowhead=7, ax=45, ay=40, arrowcolor="grey", font=sensor_font))
    fig.add_annotation(
        go.layout.Annotation(x=0.24, y=0.2, text='S3', arrowhead=7, ax=-45, ay=0, arrowcolor="grey", font=sensor_font))
    fig.add_annotation(
        go.layout.Annotation(x=0.65, y=0.7, text='S4', arrowhead=7, ax=-45, ay=20, arrowcolor="grey", font=sensor_font))
    fig.add_annotation(
        go.layout.Annotation(x=0.83, y=0.6, text='S5', arrowhead=7, ax=-75, ay=40, arrowcolor="grey", font=sensor_font))
    fig.add_annotation(
        go.layout.Annotation(x=0.74, y=0.2, text='S6', arrowhead=7, ax=65, ay=0, arrowcolor="grey", font=sensor_font))
    fig.add_trace(go.Scatter(x=[0.3, 0.16, 0.3, 0.7, 0.86, 0.7], y=[0.7, 0.6, 0.2, 0.7, 0.6, 0.2], mode='markers+text',
                             marker={'size': 43, 'color': colors}, text=sensor_values,
                             textfont={'color': 'white', 'size': 18}))
    return fig


def build_data_storage_dict():
    store = {
        'patient_id': 1,
        'uuid': None
    }
    for p_id in range(n_patients):
        store[f'patient{p_id + 1}'] = {}
        for i in range(n_traces):
            store[f'patient{p_id + 1}'][f'trace{i}'] = []
    return store


def main():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(id='header', children='walk monitoring'),
        dbc.Row([dbc.Col(children=[html.Button(f'patient id {i}', id=f'button{i}',
                                               className='patient-button') for i in range(1, 7)]),
                 dbc.Col(html.Div(id='content', children=''))])
        , html.Button('||', id='stop', className='stop-button'),
        html.Button(' > ', id='start', className='start-button'),
        html.Div(id='clock_div', children=dcc.Interval(id='clock', interval=tick_time)),
        dcc.Store('current_patient_id_input', data=build_data_storage_dict()),
        dcc.Store('current_patient_id_output', data=build_data_storage_dict()),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(
                        id='trace_left',
                        figure=create_figure_for_trace([], left_trace_range,
                                                       'Left foot sensors trace')

                    ),
                        dcc.Graph(
                            id='trace_right',
                            figure=create_figure_for_trace([], right_trace_range,
                                                           'Right foot sensors trace')
                        )
                    ], width=9),
                dbc.Col(
                    dcc.Graph(
                        id='feet',
                    ), width=3)
            ]),
        dbc.Row([
            dbc.Col(id='anomaly_display'),
            dbc.Col(dash_table.DataTable(
                id='frame',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('rows'),
                style_table={'maxHeight': '300px','overflowY': 'scroll', 'color': 'black'}

            ), width=3, className='table')
        ])

    ], className='mainDiv')

    @app.callback(
        [Output('clock_div', 'children')],
        [Input('start', 'n_clicks_timestamp'),
         Input('stop', 'n_clicks_timestamp')]
    )
    def define_stream_state(start_time, stop_time):
        start_time = start_time or 1
        stop_time = stop_time or 0
        max_val = max([start_time, stop_time])
        if start_time == max_val:
            return [dcc.Interval(id='clock', interval=tick_time)]
        else:
            return [dcc.Interval(id='clock', interval=pause_time)]

    @app.callback(
        [Output('content', 'children'),
         Output('current_patient_id_output', 'data'),
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

        buttons_times = [t1, t2, t3, t4, t5, t6]
        for i, time in enumerate(buttons_times):
            buttons_times[i] = 0 if time is None else time
        max_val = max(buttons_times)
        patient_id = buttons_times.index(max_val) + 1

        changed = patient_id != data['patient_id']

        if changed:
            data['patient_id'] = patient_id

        # url = f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{patient_id}'
        url = f'http://127.0.0.1:5000/{patient_id}'
        json_data = json.loads(requests.get(url).text)
        sensors = json_data['trace']['sensors']

        row_list = db_manager.parseJSON(json_data)
        db_manager.insert_row(row_list)

        for i in range(n_traces):
            series = prepare_and_rotate_array(data[f'patient{patient_id}'][f'trace{i}'], sensors[i]['value'])
            data[f'patient{patient_id}'][f'trace{i}'] = series
        traces = data[f'patient{patient_id}']
        fig_left = create_figure_for_trace([traces[f'trace{i}'] for i in left_trace_range], left_trace_range,
                                           'left foot sensors trace')
        fig_right = create_figure_for_trace([traces[f'trace{i}'] for i in right_trace_range], right_trace_range,
                                            'right foot sensors trace')
        fig_feet = create_figure_for_feet(sensors)

        return html.Div([
            html.H2(f'patient name: {json_data["firstname"]} {json_data["lastname"]}',
                    style={'font-family': "Courier New, monospace"}),
        ], className='patientName'), data, fig_left, fig_right, fig_feet

    @app.callback(
        Output('current_patient_id_input', 'data'),
        [Input('current_patient_id_output', 'data')]
    )
    def store_current_patient_id(data):
        return data

    @app.callback(Output('anomaly_display', 'children'), [Input('frame', 'active_cell')])
    def display_anomaly(row_dict):
        if not row_dict:
            row_dict = {'row': 'no row selected', 'column_id': 'no column id'}
        return html.Div(children=f'row: {row_dict["row"]}, columns: {row_dict["column_id"]}')

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
