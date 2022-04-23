from stocks_simulation import model
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pdb



########################################################################################################################
## Web App
########################################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([html.H1('Simulation of stock paths', style={'text-align': 'center', 'font-family':'verdana'}),\
                       html.H5('Generate stock paths according to different stochastic processes',\
                               style={'text-align': 'center','font-family':'verdana'}),\
                       dcc.Markdown('Select a process: ', style={'text-align': 'left', 'font-family': 'verdana'}),\
                       dcc.RadioItems(id='process',options=[{'label': x, 'value': x} for x in\
                                                            ['black-scholes', 'heston']],\
                                      value='black-scholes',style={'text-align': 'left', 'font-family': 'verdana',\
                                                                   'display': 'inline-block'},\
                                      inputStyle={'margin': '10px'}),\
                       html.Br(),\
                       dcc.Dropdown(multi=False, style={'text-align': 'left', 'font-family': 'verdana'},\
                                    id='model_specification'), \
                       html.Br(),\
                       html.Div(id='model_parameters'),\
                       html.Br(),\
                       dcc.Graph(id='stock_path')])


@app.callback(
    [Output('model_specification', 'options'),\
     Output('model_specification', 'value')],\
        Input('process', 'value'))
def dropdown_options(process):
    if process == 'black-scholes':
        options_dd = {model_specification: model_specification for model_specification in ['no-jump','merton']}
    elif process == 'heston':
        options_dd = {model_specification: model_specification for model_specification in ['no-jump','bates']}
    value = options_dd[list(options_dd.keys())[0]]
    return options_dd, value

@app.callback(
    Output('model_parameters','children'),
    [Input('process','value'),\
     Input('model_specification','value')]
)
def parameters_ls(process,model_specification):
    params_ls = [dcc.Input(id='S0', placeholder='Insert S0', min=0.00, step=1, size='md', type='number',debounce=True),\
                 dcc.Input(id='r', min=0.00, step=.01, size='md', placeholder='Insert r',type='number',debounce=True)]
    if process == 'black-scholes':
        process_param_ls = [dcc.Input(id='vol',min=0.00,step=.01,size='md',placeholder='Insert vol',type='number',\
                                       debounce=True)]
        if model_specification == 'no-jump':
            add_param_ls = []
        elif model_specification == 'merton':
            add_param_ls = [dcc.Input(id='jump_intensity',placeholder='Insert jump_intensity',min=0.00,step=1,\
                                      size='md',type='number',debounce=True),\
                            dcc.Input(id='mu_j', min=0.00, step=.1, size='md',\
                                      placeholder='Insert mu_j',type='number',debounce=True), \
                            dcc.Input(id='vol_j',min=0.00,step=.1,size='md',placeholder='Insert vol_j',\
                                      type='number',debounce=True,)]
    elif process == 'heston':
        process_param_ls = [dcc.Input(id='speed', placeholder='Insert k', min=0.00, step=.1, \
                                  size='md', type='number', debounce=True), \
                            dcc.Input(id='mean', min=0.00, step=.1, size='md', \
                                      placeholder='Insert mean of vol', type='number', debounce=True), \
                            dcc.Input(id='vol_of_vol', min=0.00, step=.1, size='md', placeholder='Insert vol of vol', \
                                      type='number', debounce=True), \
                            dcc.Input(id='corr', min=0.00, step=.1, size='md', placeholder='Insert corr', \
                                      type='number', debounce=True)]
        if model_specification == 'no-jump':
            add_param_ls = []
        elif model_specification == 'bates':
            add_param_ls = [dcc.Input(id='jump_intensity', placeholder='Insert jump_intensity', min=0.00, step=1, \
                                      size='40', type='number', debounce=True), \
                            dcc.Input(id='mu_j', min=0.00, step=.1, size='md', \
                                      placeholder='Insert mu_j', type='number', debounce=True), \
                            dcc.Input(id='vol_j', min=0.00, step=.1, size='md', placeholder='Insert vol_j', \
                                      type='number', debounce=True)]
    else:
        pass
    return params_ls+process_param_ls+add_param_ls

@app.callback(
   Output('stock_path', 'figure'),
   [Input('process', 'value'),
    Input('model_specification', 'value'),\
    Input('S0', 'value'),\
    Input('r', 'value'),\
    Input('vol', 'value')])
def simulation(process,model_specification,S0,r,vol):

    if (S0 == None)|(r == None)|(vol == None):
        S0 = 100
        r = 0.05
        vol = 0.2
        stock_sim = model(process=process,r=r,vol=vol,S0=S0)
    else:
        stock_sim = model(process=process,r=r,vol=vol,S0=S0)

    df = stock_sim.create_path(model_specification)
    if process == 'black-scholes':
        if model_specification == 'no-jump':
            df = stock_sim.create_path(model_specification)
        elif model_specification == 'merton':
            df = stock_sim.create_path(model_specification,1,0.5,0.2)
        fig = px.line(df, title='Monte Carlo simulation', labels={'value': 'Prices', 'index': 'Time'})
        return fig
    elif process == 'heston':
        stock_sim = model(process=process)
        if model_specification == 'no-jump':
            df = stock_sim.create_path(model_specification,0.5,1,0.5,0.2)
        elif model_specification == 'bates':
            df = stock_sim.create_path(model_specification,0.5,1,0.5,0.2,1,0.5,0.2)
    fig = px.line(df, title='Monte Carlo simulation', labels={'value': 'Prices', 'index': 'Time'})
    return fig


########################################################################################################################
## Main
########################################################################################################################

if __name__ == '__main__':
    app.run_server(debug=True,port=1111)