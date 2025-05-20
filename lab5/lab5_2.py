import numpy as np
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, filtfilt

INIT_AMPLITUDE = 1.0
INIT_FREQ = 1.0
INIT_PHASE = 0.0
INIT_NOISE_MEAN = 0.0
INIT_NOISE_STD = 0.1
FILTER_WINDOW_INIT = 10

t = np.linspace(0, 2 * np.pi, 500)
initial_noise = np.random.normal(INIT_NOISE_MEAN, INIT_NOISE_STD, size=t.shape)

def ma_filter(signal, window_size):
    window_size = int(window_size)
    return uniform_filter1d(signal, size=window_size, mode='nearest')

def butterworth_filter(signal, cutoff_freq, fs, window_size):
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(window_size, normal_cutoff, btype='low')
    filtered = filtfilt(b, a, signal)
    return filtered

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        dcc.Graph(id='raw-signal-graph', style={'width':'48%', 'display':'inline-block'}),
        dcc.Graph(id='filtered-signal-graph', style={'width':'48%', 'display':'inline-block'})
    ]),
    html.Div([
        html.Label("Амплітуда:"),
        dcc.Slider(id='amplitude', min=0, max=10, step=0.1, marks={0:'0',5:'5',10:'10'}, value=INIT_AMPLITUDE, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Label("Частота:"),
        dcc.Slider(id='frequency', min=0.1, max=10, step=0.1, marks={0.1:'0.1',5:'5',10:'10'}, value=INIT_FREQ, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Label("Фаза:"),
        dcc.Slider(id='phase', min=0, max=2*np.pi, step=0.1, marks={0:'0',3.14:'π',6.28:'2π'}, value=INIT_PHASE, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Label("Середнє шуму:"),
        dcc.Slider(id='noise-mean', min=-1, max=1, step=0.05, marks={-1:'-1',0:'0',1:'1'}, value=INIT_NOISE_MEAN, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Label("Стандартне відхилення шуму:"),
        dcc.Slider(id='noise-std', min=0, max=1.0, step=0.05, marks={0:'0',0.5:'0.5',1:'1'}, value=INIT_NOISE_STD, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Label("Показати шум:"),
        dcc.Checklist(id='show-noise', options=[{'label':'Так','value':'show'}], value=['show'], inline=True),
        html.Label("Тип фільтра:"),
        dcc.Dropdown(id='filter-type', options=[{'label': 'Moving Average', 'value': 'MA'}, {'label': 'Butterworth', 'value': 'BW'}], value='MA', clearable=False),
        html.Label("Розмір вікна фільтра:"),
        dcc.Slider(id='filter-window', min=1, max=50, step=1, marks={1:'1', 25:'25', 50:'50'}, value=FILTER_WINDOW_INIT, tooltip={"always_visible": False, "placement": "bottom"}),
        html.Button('Reset', id='reset-btn', n_clicks=0)
    ], style={'width':'70%', 'margin':'auto', 'padding':'20px'})
])

@app.callback(
    [Output('raw-signal-graph','figure'), Output('filtered-signal-graph','figure')],
    [Input('amplitude','value'), Input('frequency','value'), Input('phase','value'),
     Input('noise-mean','value'), Input('noise-std','value'), Input('show-noise','value'),
     Input('filter-type','value'), Input('filter-window','value'), Input('reset-btn','n_clicks')]
)
def update_graphs(amplitude, frequency, phase, noise_mean, noise_std, show_noise_list, filter_type, window_size, n_clicks):

    show_noise = 'show' in show_noise_list

    global initial_noise
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered in ['noise-mean','noise-std','reset-btn']:
        initial_noise = np.random.normal(noise_mean, noise_std, size=t.shape)

    pure = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    raw_signal = pure + initial_noise if show_noise else pure

    if filter_type == 'MA':
        filt_signal = ma_filter(raw_signal, window_size)
    elif filter_type == 'BW':
        dt = t[1] - t[0]
        fs = 1.0 / dt
        cutoff_freq = min(fs / window_size, 0.99 * fs / 2)
        filt_signal = butterworth_filter(raw_signal, cutoff_freq=cutoff_freq, fs=fs, window_size=window_size)
    else:
        filt_signal = raw_signal

    raw_fig = go.Figure(data=[go.Scatter(x=t, y=raw_signal, mode='lines', name='Raw signal')])
    raw_fig.update_layout(title='Зашумлений графік', xaxis_title='Час', yaxis_title='Амплітуда', template='plotly_white')

    filt_fig = go.Figure(data=[go.Scatter(x=t,y=filt_signal,mode='lines',name='Filtered signal')])
    filt_fig.update_layout(title='Фільтрований графік', xaxis_title='Час', yaxis_title='Амплітуда', template='plotly_white')

    return raw_fig, filt_fig


@app.callback(
    [Output('amplitude','value'),Output('frequency','value'),Output('phase','value'),
     Output('noise-mean','value'),Output('noise-std','value'),Output('show-noise','value'),
     Output('filter-type','value'),Output('filter-window','value')],
    [Input('reset-btn','n_clicks')]
)
def reset_controls(n_clicks):
    if n_clicks > 0:
        return INIT_AMPLITUDE, INIT_FREQ, INIT_PHASE, INIT_NOISE_MEAN, INIT_NOISE_STD, ['show'], 'MA', FILTER_WINDOW_INIT
    raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    app.run(debug=True)