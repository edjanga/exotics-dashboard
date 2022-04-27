from stocks_simulation import model
from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL
import plotly.express as px
import pdb



########################################################################################################################
## Web App
########################################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([html.H1('Simulation of stock paths', style={'text-align': 'center', 'font-family': 'verdana'}), \
                       html.H5('Generate stock paths according to different stochastic processes', \
                               style={'text-align': 'center', 'font-family': 'verdana'}), \
                       dcc.Markdown('Select a process: ', style={'text-align': 'left', 'font-family': 'verdana'}), \
                       html.Div( \
                           dcc.RadioItems(id='process', options=[{'label': x, 'value': x} for x in \
                                                                 ['black-scholes', 'heston']], \
                                          value='black-scholes', style={'text-align': 'left', 'font-family': 'verdana', \
                                                                        'display': 'inline-block'}, \
                                          inputStyle={'margin': '10'}), style={'display': 'inline-block'}), \
                       dcc.Dropdown(multi=False, style={'text-align': 'left', 'font-family': 'verdana'}, \
                                    id='model_specification'), \
                       html.Br(), \
                       html.Div(id='main_container')])


@app.callback(
    [Output('model_specification', 'options'), \
     Output('model_specification', 'value')], \
        Input('process', 'value'))
def dropdown_options(process):
    if process == 'black-scholes':
        options_dd = {model_specification: model_specification for model_specification in ['no-jump', 'merton']}
    elif process == 'heston':
        options_dd = {model_specification: model_specification for model_specification in ['no-jump', 'bates']}
    value = options_dd[list(options_dd.keys())[0]]
    return options_dd, value


@app.callback(
    Output('main_container', 'children'), \
        [Input('process', 'value'), \
         Input('model_specification', 'value')], \
        State('main_container', 'children')
)
def generate_paths(process, model_specification, div_children):
    div_children = []
    params_ls = [dcc.Input(id={'type': 'input', 'index': 0}, placeholder='Insert S0', min=0.00, step=1, size='md', \
                           type='number', value=0, debounce=True), \
                 dcc.Input(id={'type': 'input', 'index': 1}, min=0.00, step=.01, size='md', placeholder='Insert r', \
                           type='number', value=0, debounce=True)]
    if process == 'black-scholes':
        process_param_ls = [dcc.Input(id={'type': 'input', 'index': 2}, min=0.00, step=.01, size='md', \
                                      placeholder='Insert vol', type='number', debounce=True, value=0)]

        if model_specification == 'merton':
            model_specification_param_ls = [dcc.Input(id={'type': 'input', 'index': 3}, \
                                                      placeholder='Insert jump_intensity',
                                                      min=0.00, step=1, size='40', type='number', debounce=True, \
                                                      value=0), \
                                            dcc.Input(id={'type': 'input', 'index': 4}, min=0.00, step=.1, size='md', \
                                                      placeholder='Insert mu_j', type='number', \
                                                      debounce=True, value=0), \
                                            dcc.Input(id={'type': 'input', 'index': 5}, min=0.00, step=.1, size='md', \
                                                      placeholder='Insert vol_j', \
                                                      type='number', debounce=True, value=0)]
        else:
            model_specification_param_ls = []
    elif process == 'heston':
        process_param_ls = [dcc.Input(id={'type': 'input', 'index': 2}, placeholder='Insert k', min=0.00, step=.1, \
                                      size='md', type='number', debounce=True, value=0), \
                            dcc.Input(id={'type': 'input', 'index': 3}, min=0.00, step=.1, size='md', \
                                      placeholder='Insert mean of vol', type='number', debounce=True, value=0), \
                            dcc.Input(id={'type': 'input', 'index': 4}, min=0.00, step=.1, size='md', \
                                      placeholder='Insert vol of vol', \
                                      type='number', debounce=True, value=0), \
                            dcc.Input(id={'type': 'input', 'index': 5}, min=0.00, step=.1, \
                                      size='md', placeholder='Insert corr', type='number', debounce=True, value=0)]

        if model_specification == 'bates':
            model_specification_param_ls = [dcc.Input(id={'type': 'input', 'index': 6}, \
                                                      placeholder='Insert jump_intensity',
                                                      min=0.00, step=1, size='40', type='number', debounce=True, \
                                                      value=0), \
                                            dcc.Input(id={'type': 'input', 'index': 7}, min=0.00, step=.1, size='md', \
                                                      placeholder='Insert mu_j', type='number', \
                                                      debounce=True, value=0), \
                                            dcc.Input(id={'type': 'input', 'index': 8}, min=0.00, step=.1, size='md', \
                                                      placeholder='Insert vol_j', \
                                                      type='number', debounce=True, value=0)]
        else:
            model_specification_param_ls = []
    div_children.append(html.Div(params_ls + process_param_ls + model_specification_param_ls))
    ####################################################################################################################
    ## Display figure
    ####################################################################################################################
    graph_comp = dcc.Graph(id='simulation', figure={})
    div_children.append(graph_comp)
    return div_children


@app.callback(
    Output('simulation', 'figure'),
    [Input('process', 'value'), \
     Input('model_specification', 'value'), \
     Input(component_id={'type': 'input', 'index': ALL}, component_property='value')],
    State('simulation', 'figure')
)
def update_graph(process, model_specification, *args):
    stock_sim = model(process=process, S0=args[0][0], r=args[0][1])
    if process == 'black-scholes':
        if model_specification == 'no-jump':
            df = stock_sim.create_path(model_specification, args[0][2])
        elif model_specification == 'merton':
            try:
                df = stock_sim.create_path(model_specification, args[0][2], args[0][3], args[0][4], args[0][5])
            except IndexError:
                df = stock_sim.create_path(model_specification, args[0][2], 0, 0, 0)
    elif process == 'heston':
        if model_specification == 'no-jump':
            try:
                df = stock_sim.create_path(model_specification, args[0][2], args[0][3], args[0][4], args[0][5])
            except IndexError:
                df = stock_sim.create_path(model_specification, args[0][2], 0, 0, 0)
        elif model_specification == 'bates':
            try:
                df = stock_sim.create_path(model_specification, args[0][2], args[0][3], args[0][4], \
                                           args[0][5], args[0][6], args[0][7])
            except IndexError:
                df = stock_sim.create_path(model_specification, args[0][2], 0, 0, 0, 0, 0)
    fig = px.line(df, title='Monte Carlo simulation', labels={'value': 'Prices', 'index': 'Time'})
    return fig

########################################################################################################################
## Main
########################################################################################################################

if __name__ == '__main__':
    app.run_server(debug=False)
