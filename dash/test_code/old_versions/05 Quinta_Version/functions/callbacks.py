import json
from dash import Dash, dcc
import pandas as pd
from dash.dependencies import Input, Output

from functions.grafics import *
from functions.columns import *
from functions.table import *
from functions.finalarchive import *

app = Dash(__name__,suppress_callback_exceptions=True)
app.title = "IBRN"

#LLamada para obtener las posibles graficas de acuerdo a la categoria seleccionada
@app.callback(
    Output("possible_plots", "children"),
    Input("possible_categories", "value")
)
def select_graphs(value):
    """
    Actualiza el contenido del componente de Dash "possible_plots" con un elemento 
    dcc.Dropdown que contiene las opciones de gráficos correspondientes a la categoría 
    seleccionada en el componente "possible_categories".

    Args:
        value (str): 
            La categoría seleccionada en el componente "possible_categories".

    Returns:
        values_dropdown (dcc.Dropdown): 
            Componente de Dash que contiene las opciones de gráficos correspondientes a la categoría seleccionada.

    """
    opt_values = climatic_categories[value]

    if value=="Otros":
        initial = [opt_values[0]]
    else:
        initial = opt_values

    len_options = len(opt_values)
    if len_options>=5:
        len_options=5

    values_dropdown = dcc.Checklist(id="graph_values",
                                    options=opt_values,
                                    value=initial,
                                    labelStyle={"display": "flex", "align-items": "center"},
                                    style={"maxWidth": "1000px", "columnCount":len_options}
                                    )
    return values_dropdown




    

#Indicador para grafica
@app.callback(Output('indicator_graphic', 'figure'),
              Input("possible_categories", "value"),
              Input('graph_values', 'value'),
              Input('my_date_picker_range', 'start_date'),
              Input('my_date_picker_range', 'end_date'))
def update_time_range_slider(categorie,selected_values,start_date,end_date):
    """
    Actualiza el gráfico del indicador en la aplicación Dash.

    Args:
        categorie (str):
            Categoria seleccionada.
        selected_values (list): 
            Valores seleccionados en el componente 'graph_values'.
        start_date (str): 
            Fecha de inicio seleccionada en el componente 'my_date_picker_range' en formato 'YYYY-MM-DD'.
        end_date (str): 
            Fecha de fin seleccionada en el componente 'my_date_picker_range' en formato 'YYYY-MM-DD'.

    Returns:
        fig (go.Figure):
            Objeto que contiene el gráfico del indicador actualizado.
    """

    figure_width = 650

    
    fig = make_graphic(categorie,selected_values,start_date,end_date)
    
    fig.update_layout(margin={'l': 50, 'b': 50, 't': 50, 'r': 50}, 
                        hovermode='x',
                        clickmode='event+select',
                        autosize=False,
                        width=int(figure_width *(16/9)),
                        height=figure_width )
    return fig


#LLamada para mostrar tabla
@app.callback(Output('table_container', 'children'),
              Input('graph_values', 'value'),
              Input('my_date_picker_range', 'start_date'),
              Input('my_date_picker_range', 'end_date'),
              Input('indicator_graphic', 'clickData'))
def update_table(y_axis_column_name, start_date, end_date, click_data):

    """
    Actualiza la tabla de datos en la aplicación Dash.

    Args:
        y_axis_column_name (str): 
            Nombre de la columna del eje Y seleccionado en el componente 'graph_values'.
        start_date (str): 
            Fecha de inicio seleccionada en el componente 'my_date_picker_range' en formato 'YYYY-MM-DD'.
        end_date (str): 
            Fecha de fin seleccionada en el componente 'my_date_picker_range' en formato 'YYYY-MM-DD'.
        time_range (List[int]): 
            Rango de tiempo seleccionado en el componente 'time_range_slider'.
        click_data (dict): 
            Datos seleccionados en el gráfico 'indicator_graphic'.

    Returns:
        dbc.Table:
            Tabla de datos actualizada.
    """
        
    days = pd.to_datetime(end_date) - pd.to_datetime(start_date)
    days = days.days

    if click_data != None:
        a = json.dumps(click_data, indent=2)
        diccionario = json.loads(a)
        click_data = diccionario["points"][0]["x"]

    if days == 1:
        return create_table(y_axis_column_name, start_date, end_date, highlight_date=click_data)
    else:
        return create_table(y_axis_column_name, start_date, end_date, highlight_date=click_data)
    

@app.callback(
Output('output', 'children'),
Input('mes', 'value'),)
def update_output(value):
    generate(value)