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

columns = [{"name": i, "id": i} for i in ['index', 'date', 'sensors']]
patient_names = {1: 'Janek Grzegorczyk', 2: 'Elżbieta Kochalska', 3: 'Albert Lisowski', 4: 'Ewelina Nosowska',
                 5: 'Piotr Fokalski', 6: 'Bartosz Moskalski'}

x_range = 600
n_traces = 6
n_patients = 6
left_trace_range = range(3)
right_trace_range = range(3, 6)
feet_img = base64.b64encode(open('feet.png', 'rb').read())
tick_time = 1000
pause_time = 60 * 60 * 1000

colsize = 5

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
    return dcc.Graph(
        figure={
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
                    'tick0': 0,
                    'dtick': 200,
                    # 'type': "log"
                },
                'xaxis': {'color': 'white', 'tickmode': 'array', 'tickvals': np.arange(0, 600, 100),
                          'ticktext': np.arange(600, 0, -100)},
                'height': 300,
                'plot_bgcolor': 'black',
                'paper_bgcolor': 'black',
                'font': {'family': 'Courier New, monospace', 'color': 'white', 'size': 15}
            }
        }
    )


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
        'selected_anomaly_row': None
    }
    for p_id in range(1, n_patients + 1):
        store[f'patient{p_id}'] = {}
        store[f'patient{p_id}']['anomalies_data'] = []
        for i in range(n_traces):
            store[f'patient{p_id}'][f'trace{i}'] = []
    return store


def build_anomalies_frame(list_of_rows_dicts):
    df = pd.DataFrame(list_of_rows_dicts)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)
    df = df.reset_index(drop=True)
    df['index'] = df.index
    return df.to_dict('rows')


def serve_layout():
    session_id = str(uuid.uuid4())
    while session_id in db_managers:
        session_id = str(uuid.uuid4())
    db_managers[session_id] = DashDBmanager(db_path)
    return html.Div(children=[
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.H1(id='header', children='walk monitoring'),
        dbc.Row([dbc.Col(children=[html.Button(f'patient id {i}', id=f'button{i}',
                                               className='patient-button') for i in range(1, 7)]),
                 dbc.Col(html.Div(id='content', children=''))])
        , html.Button('||', id='stop', className='stop-button'),
        html.Button(' > ', id='start', className='start-button'),
        html.Div(id='clock_div', children=dcc.Interval(id='clock', interval=tick_time)),
        dcc.Store('current_user_cache_input', data=build_data_storage_dict()),
        dcc.Store('current_user_cache_output', data=build_data_storage_dict()),
        dbc.Row(
            [
                dbc.Col(
                    [html.Div(id='trace_left'), html.Div(id='trace_right'),
                     ], width=9),
                dbc.Col(
                    dcc.Graph(
                        id='feet',
                    ), width=3)
            ]),
        dbc.Row([
            dbc.Col([html.Div(id='anomaly_display_left'), html.Div(id='anomaly_display_right')]),
            dbc.Col(dash_table.DataTable(
                id='frame',
                columns=columns,
                data=[{}],
                style_table={'maxHeight': '300px', 'overflowY': 'scroll', 'color': 'black', 'whiteSpace': 'normal'},
                style_cell={
                    'minWidth': f'{20}px', 'maxWidth': f'{80}px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                }

            ), width=3, className='table')
        ])

    ], className='mainDiv')


def main():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = serve_layout()

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
         Output('current_user_cache_output', 'data'),
         Output('trace_left', 'children'),
         Output('trace_right', 'children'),
         Output('feet', 'figure'),
         Output('frame', 'data')],
        [Input('clock', 'n_intervals'),
         *[Input(f'button{i}', 'n_clicks_timestamp') for i in range(1, 7)],
         Input('session-id', 'children')
         ],
        [State('current_user_cache_input', 'data')]

    )
    def tick(_, t1, t2, t3, t4, t5, t6, session_id, data):
        db_manager = db_managers[session_id]

        buttons_times = [t1, t2, t3, t4, t5, t6]
        for i, time in enumerate(buttons_times):
            buttons_times[i] = 0 if time is None else time
        max_val = max(buttons_times)
        patient_id = buttons_times.index(max_val) + 1
        url = f'http://127.0.0.1:5000/{patient_id}'
        json_data = json.loads(requests.get(url).text)

        changed = patient_id != data['patient_id']

        if changed:
            data['patient_id'] = patient_id
        if not data[f'patient{patient_id}']['anomalies_data']:
            data[f'patient{patient_id}']['anomalies_data'] = build_anomalies_frame(
                db_manager.list_anomalies(f'{json_data["firstname"]} {json_data["lastname"]}'))
        # url = f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{patient_id}'
        sensors = json_data['trace']['sensors']

        row_list = db_manager.parseJSON(json_data)
        db_manager.insert_row(row_list)

        patient_data = data[f'patient{patient_id}']
        for i in range(n_traces):
            series = prepare_and_rotate_array(patient_data[f'trace{i}'], sensors[i]['value'])
            data[f'patient{patient_id}'][f'trace{i}'] = series

        fig_left = create_figure_for_trace([patient_data[f'trace{i}'] for i in left_trace_range], left_trace_range,
                                           'left foot sensors trace')
        fig_right = create_figure_for_trace([patient_data[f'trace{i}'] for i in right_trace_range], right_trace_range,
                                            'right foot sensors trace')
        fig_feet = create_figure_for_feet(sensors)

        return html.Div([
            html.H2(f'patient name: {json_data["firstname"]} {json_data["lastname"]}',
                    style={'font-family': "Courier New, monospace"}),
        ], className='patientName'), data, fig_left, fig_right, fig_feet, data[f'patient{patient_id}']['anomalies_data']

    @app.callback([Output('anomaly_display_left', 'children'), Output('anomaly_display_right', 'children')],
                  [Input('frame', 'active_cell')],
                  [State('frame', 'data'), State('current_user_cache_output', 'data'), State('session-id', 'children')])
    def display_anomaly(row_dict, list_of_row_dicts, data_store, session_id):
        if not row_dict:
            return [html.H3(children='no anomaly selected'), '']
        row_id = row_dict['row']
        if data_store['selected_anomaly_row'] != row_id:
            data_store['selected_anomaly_row'] = row_id
            date = list_of_row_dicts[int(row_id)]['date']
            anomaly_trace_data = db_managers[session_id].select_area(date, patient_names[data_store['patient_id']], 30)
        anomaly_fig_l = create_figure_for_trace([anomaly_trace_data[i] for i in left_trace_range], left_trace_range,
                                                'left anomaly')
        anomaly_fig_r = create_figure_for_trace([anomaly_trace_data[i] for i in right_trace_range], right_trace_range,
                                                'right anomaly')
        return [anomaly_fig_l, anomaly_fig_r]

    @app.callback(
        Output('current_user_cache_input', 'data'),
        [Input('current_user_cache_output', 'data')]
    )
    def store_current_patient_id(data):
        return data

    app.run_server(debug=True)



if __name__ == '__main__':
    main()
