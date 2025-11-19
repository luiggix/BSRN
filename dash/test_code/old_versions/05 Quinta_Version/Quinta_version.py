from dash import dcc, html
from dash.dependencies import Input, Output, State

from functions.grafics import *
from functions.columns import *
from functions.table import *
from functions.callbacks import *

################################################
#  Creacion de objetos Iniciales para mostrar  #
################################################

# Grafica a Mostrar
dropdown_categorias = dcc.Dropdown(names_categories,
                    'Parametros Basicos',
                    id="possible_categories",
                    style={'width': '400px'},
                    multi=False,
                    searchable=True
                    )

# Rango de Fechas
rang_date = dcc.DatePickerRange(id='my_date_picker_range',
                                min_date_allowed=df['TIMESTAMP'][0],
                                max_date_allowed=df['TIMESTAMP'].iloc[-1],
                                initial_visible_month=df['TIMESTAMP'][0],
                                start_date=df['TIMESTAMP'][0],
                                end_date=df['TIMESTAMP'][1440]) 


dropdown_graph_values = dcc.Dropdown(id='graph_values')

opciones = [{'label': str(i), 'value': i} for i in range(5, 12)]
mounths=dcc.Dropdown(
            id='mes',
            options=opciones,
            value=5
        )

##################################################
#               Pantalla principal               #
##################################################

app.layout = html.Div([
    html.H1("BSRN IGEF"),

    html.Hr(),

    html.Div([
        html.H3("Seleccione la categoria"),
        dropdown_categorias],
        style={'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}
        ),

    html.Hr(),
    html.H3("Seleccione las graficas a mostrar"),
    html.Div(
        dropdown_graph_values,
        id = "possible_plots",
        style= {'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),

    html.Hr(),

    html.Div(
        [
            html.H3("Seleccione el perido de fechas deseado"),
            rang_date
        ],
        style={'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),

    html.Br(),

    html.Hr(),
    dcc.Graph(id='indicator_graphic'),

    html.Hr(),
    html.H3("Datos totales"),
    html.Div(id='table_container'),

    html.Hr(),
    html.H2("Generar arhivo final"),
    html.H3("Seleccione el mes"),
    html.Br(),
    html.Div(mounths),
    html.Button('Generar archivo', id='my-button', n_clicks=0),
    html.Div(id='output')

],style={"text-align": "center","align-items": "center"})


#####################################################################
#                             Llamadas                              #
#####################################################################

    
if __name__ == '__main__':
    app.run_server(debug=True)