from stocks_simulation import model
from dash import Dash, dcc, html, Input, Output
import plotly.express as px



########################################################################################################################
## Web App
########################################################################################################################

app = Dash(__name__)
server = app.server
app.layout = html.Div([html.H1('Simulation of stock paths', style={'text-align': 'center', 'font-family':'verdana'}),\
                       html.H5('Generate stock paths according to different stochastic processes',\
                               style={'text-align': 'center','font-family':'verdana'}),\
                       dcc.Markdown('Select a process: ', style={'text-align': 'left', 'font-family': 'verdana'}),\
                       dcc.RadioItems(id='process',options=[{'label': x, 'value': x} for x in\
                                                            ['black-scholes', 'heston']],\
                                      value='black-scholes',style={'text-align': 'left', 'font-family': 'verdana'},\
                                      inputStyle={'margin': '10px'}),\
                       html.Br(),\
                       dcc.Dropdown(multi=False, style={'text-align': 'left', 'font-family': 'verdana'},\
                                    id='model_specification'),\
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
        options_dd = {model_specification: model_specification for model_specification in ['no-jump']}
    value = options_dd[list(options_dd.keys())[0]]
    return options_dd, value

@app.callback(
   Output('stock_path', 'figure'),
   [Input('process', 'value'),
    Input('model_specification', 'value')])
def simulation(process, model_specification):
    if process == 'black-scholes':
        stock_sim = model(process=process)
        if model_specification == 'no-jump':
            df = stock_sim.create_path(model_specification)
        elif model_specification == 'merton':
            df = stock_sim.create_path(model_specification,1, 0.5, 0.2)
    elif process == 'heston':
        stock_sim = model(process=process)
        if model_specification == 'no-jump':
            df = stock_sim.create_path(model_specification, 0.5, 1, 0.5, 0.2)
        else:
            df = stock_sim.create_path(model_specification, 0.5, 1, 0.5, 0.2, 0.1, 1)
    else:
        pass
    fig = px.line(df, title='Monte Carlo simulation', labels={'value':'Prices','index':'Time'})
    return fig

########################################################################################################################
## Main
########################################################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)