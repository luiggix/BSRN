import json
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from dash import dash_table
from plotly.subplots import make_subplots
import numpy as np 

#############################################
#  Definicion de Datos y categorias a usar  #
#############################################

# Importamos el DataFrame
df = pd.read_csv("bsrn/bsrn.csv")

# Conversion de columna 'TIMESTAMP' al formato de fecha de pandas (datatime64)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%Y-%m-%d %H:%M:%S')
start_date = df['TIMESTAMP'][0]
end_date = df['TIMESTAMP'].iloc[-1]

#Conversion de tempartura a Grados Kelvin
df['CRPTemp_Avg']=df['CRPTemp_Avg']+273.15
df['UVTEMP_Avg']=df['UVTEMP_Avg']+273.15
df["DEW_POINT_Avg"] = df["DEW_POINT_Avg"]+273.15

# Guardamos todas las culumnas del DataFrame
columns=[]
for i in df.columns:
    columns.append(i)

# Columnas provicionales para trabajar
avg_list = [x.replace("_Avg","") for x in columns if x.endswith("Avg")]
std_list = [x.replace("_Std","") for x in columns if x.endswith("Std")]
min_list = [x.replace("_Min","") for x in columns if x.endswith("Min")]
max_list = [x.replace("_Max","") for x in columns if x.endswith("Max")]

common_list = list(set(avg_list) & set(std_list) & set(min_list) & set(max_list))

aux = [elemento + "_" + str(i) for elemento in common_list for i in ["Avg","Std","Min","Max"]]
unique_columns=columns.copy()
for i in aux:
    unique_columns.remove(i)

unique_columns.remove("TIMESTAMP")
unique_columns.remove("RECORD")

merged_columns = unique_columns+common_list


basic_parameters = ["GLOBAL","DIRECT","DIFFUSE","GH_CALC_Avg"]
shortwave_balance = ["GLOBAL","UPWARD_SW"]
longwave_balance = ["DOWNWARD","UPWARD_LW","DWIRTEMP","UWIRTEMP","CRPTemp_Avg"]
meteorology = ["CRPTemp_Avg","RELATIVE_HUMIDITY_Avg","PRESSURE_Avg","DEW_POINT_Avg"]
ultraviolet = ["UVB","UVTEMP_Avg","UVSIGNAL_Avg"]

categories = [basic_parameters,shortwave_balance,longwave_balance,meteorology,ultraviolet]

others = merged_columns.copy()

for j in categories:
    for i in j:
        if i in others:
            others.remove(i)

categories.append(others)

names_categories=["Parametros Basicos","Balance de onda corta","Balance de onda larga","Meteorologia","Ultravioleta","Otros"]

climatic_categories = dict(zip(names_categories,categories))
    
############################################
#             Comienzo de Dash             #
############################################

app = Dash(__name__,suppress_callback_exceptions=True)


############################################
#Creacion de objetos Iniciales para mostrar
############################################

# Grafica a Mostrar
dropdown_categorias = dcc.Dropdown(names_categories,
                    'Parametros Basicos',
                    id="Posibles_Categorias",
                    style={'width': '400px'},
                    multi=False,
                    searchable=True
                    )

# Rango de Fechas
rang_date = dcc.DatePickerRange(id='my-date-picker-range',
                                min_date_allowed=df['TIMESTAMP'][0],
                                max_date_allowed=df['TIMESTAMP'].iloc[-1],
                                initial_visible_month=df['TIMESTAMP'][0],
                                start_date=df['TIMESTAMP'][0],
                                end_date=df['TIMESTAMP'][1440]) 

#Rango de Tiempo
rang_time = dcc.RangeSlider(
        id='time-range-slider',
        min=0,
        max=1440,
        value=[0,1440],
        marks={i*60: "{}:00".format(i) for i in range(25)}
    )

dropdown_graph_values = dcc.Dropdown(id='Valores_Graficas')

##################################################
#Pantalla principal
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
        id = "Posibles_Graficas",
        style= {'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),

    html.Hr(),

    html.Div(
        [
            html.H3("Seleccione el perido de fechas deseado"),
            rang_date
        ],
        style={'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),
    

    html.Hr(),
    
    html.H3("Seleccione el perido de tiempo deseado (Al seleccionar mas de un dia en la opción anterior, esta se desactiva)"),
    rang_time,

    html.Br(),

    html.Hr(),

    dcc.Graph(id='indicator-graphic'),

    html.Hr(),

    html.H3("Datos totales"),
    html.Div(id='table-container'),

    html.Div(id="a"),

],style={"text-align": "center","align-items": "center"})

#####################################################################
#                             Funciones                             #
#####################################################################


def grafica(df,selections,start,end,time=[0,-1]):
    #Función para graficar 
    initial = df[df['TIMESTAMP'] == start].index
    final   = df[df['TIMESTAMP'] == end].index
    dff=df[initial [0]:final[0]]

    
       #Filtros para cada variable

    #Filtros para angulo cenital menor a 90 y mayor a cero
    hour_filter = (dff["ZenDeg"]>=0) & (dff["ZenDeg"]<=90)
    filtered_dff = dff.loc[hour_filter]

    #Filtro para varible global
    global_filter = (((1366*1.017*1.2*np.cos(filtered_dff["ZenDeg"])**(1.2))+50)>=filtered_dff["GLOBAL_Avg"]) & (filtered_dff["GLOBAL_Avg"]>=-2 )
    filtered_global_correct = filtered_dff.loc[global_filter]
    merged = pd.merge(filtered_dff, filtered_global_correct, how='left', indicator=True)
    filtered_global_incorrect = merged.loc[merged['_merge'] == 'left_only']


    #Filtro para varible Difussa
    diffuse_filter = (((1366*0.95*np.cos(dff["ZenDeg"])**(1.2))+10)>=dff["DIFFUSE_Avg"]) & (dff["DIFFUSE_Avg"]>=-2 )
    filtered_diffuse = dff.loc[diffuse_filter]
    
    #Filtro para varible Directa
    direct_filter = (((1366*0.95*np.cos(dff["ZenDeg"])**(0.2))+10)>=dff["DIRECT_Avg"]) & (dff["DIRECT_Avg"]>=-2 )
    filtered_direct = dff.loc[direct_filter]

    fig = make_subplots(rows=1, cols=1)
    
    if type(selections) != list:
            selections=[selections]
            
    #Definimos el tipo de figura de acuerdo con las graficas
    if selections[-1] in (basic_parameters + shortwave_balance):
        fig = make_subplots(rows=1, cols=1)
        row_=1
        col_=1
        aux1=0
        
    elif selections[-1] in longwave_balance:
        fig = make_subplots(rows=2, cols=1)
        row_=1
        col_=1
        aux1=1

    elif selections[-1] in meteorology:
        fig = make_subplots(rows=2, cols=2)
        row_=1
        col_=1
        aux1=2
    
    elif selections[-1] in ultraviolet:
        fig = make_subplots(rows=3, cols=1)
        row_=1
        col_=1
        aux1=3
    
    elif selections[-1] in others:
        fig = make_subplots(rows=1, cols=1)
        row_=1
        col_=1
        aux1=4

    for selection in selections:

        #Opciones datos basicos
        if(aux1==0):
            fig.update_xaxes(title_text="Día, Hora", row=1, col=1)
            fig.update_yaxes(title_text="W/m^2", row=1, col=1)

        #Opciones para Balance_de_onda_larga
        if (aux1==1):
            fig.update_yaxes(title_text="Temp", row=2, col=1)
            fig.update_yaxes(title_text="W/m^2", row=1, col=1)
            fig.update_xaxes(title_text="Dia, Hora", row=2, col=1)

            if  (selection in ([longwave_balance[0]] +[longwave_balance[1]])):
                row_=1
            else:
                row_=2

        #Opciones para Meteorologia
        if (aux1==2):
            
            fig.update_yaxes(title_text="Temp (k)", row=1, col=1)
            fig.update_yaxes(title_text="%", row=2, col=1)
            fig.update_yaxes(title_text="mbar", row=1, col=2)
            fig.update_yaxes(title_text="Temp (k)", row=2, col=2)

            fig.update_xaxes(title_text="Dia, Hora", row=1, col=1)
            fig.update_xaxes(title_text="Dia, Hora", row=1, col=2)

            if selection == "CRPTemp_Avg":
                row_=1
                col_=1
            elif selection == "RELATIVE_HUMIDITY_Avg":
                row_=2
                col_=1
            elif selection == "PRESSURE_Avg":
                row_=1
                col_=2
            elif selection == "DEW_POINT_Avg":
                row_=2
                col_=2

        #Opciones para Ultravioleta
        if (aux1==3):
            fig.update_yaxes(title_text="UVB", row=1, col=1)
            fig.update_yaxes(title_text="Temp (K)", row=2, col=1)
            fig.update_yaxes(title_text="UVB", row=3, col=1)

            fig.update_xaxes(title_text="Dia, Hora", row=3, col=1)

            if selection == "UVB":
                row_=1
                col_=1
            elif selection == "UVTEMP_Avg":
                row_=2
                col_=1
            elif selection == "UVSIGNAL_Avg":
                row_=3
                col_=1

        #Opciones para Otros
        if (aux1==4):
            fig.update_yaxes(title_text=" ", row=1, col=1)
            fig.update_xaxes(title_text=" ", row=1, col=1)


        if selection in common_list:
                
            Avg = selection + "_Avg"
            Std = selection + "_Std"
            Min = selection + "_Min"
            Max = selection + "_Max"    

            if selection == "GLOBAL":
                fig.add_trace(go.Scatter(x = filtered_global_correct["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_global_correct[Avg][time[0]:time[1]],
                                    error_y = dict(type='data',array=filtered_dff[Std][time[0]:time[1]], visible=True,width=1),
                                    mode = 'lines',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = Avg),
                                    row=row_,col=col_)
                
                fig.add_trace(go.Scatter(x = filtered_global_incorrect["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_global_incorrect[Avg][time[0]:time[1]],
                                    error_y = dict(type='data',array=filtered_dff[Std][time[0]:time[1]], visible=True,width=1),
                                    mode = 'markers',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = Avg),
                                    row=row_,col=col_)
            else:
                fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                        y = filtered_dff[Avg][time[0]:time[1]],
                                        error_y = dict(type='data',array=filtered_dff[Std][time[0]:time[1]], visible=True,width=1),
                                        mode = 'lines',
                                        line=dict(width=1),
                                        connectgaps=False,
                                        name = Avg),
                                        row=row_,col=col_)
                fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                        y = filtered_dff[Min][time[0]:time[1]],
                                        mode = 'lines',
                                        line=dict(width=1),
                                        name = Min,
                                        connectgaps=False,
                                        visible = "legendonly"),
                                        row=row_,col=col_)
                fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                        y = filtered_dff[Max][time[0]:time[1]],
                                        mode = 'lines',
                                        line=dict(width=1),
                                        connectgaps=False,
                                        name = Max,
                                        visible = "legendonly"),
                                        row=row_,col=col_)
            
        elif selection in unique_columns:
            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_dff[selection][time[0]:time[1]],
                                    mode = 'lines',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = str(selection)),
                                    row=row_,col=col_)
        
    return fig


#Tabla 
def Tabla(selecciones,start,end,time=[0,-1],punto=None):

    columnas=["TIMESTAMP"]

    inicial = df[df['TIMESTAMP'] == start].index
    final   = df[df['TIMESTAMP'] == end].index
    dff=df[inicial[0]:final[0]]

    if type(selecciones) != list:
            selecciones=[selecciones]

    for seleccion in selecciones:
        if seleccion in common_list:
            for i in ["_Avg","_Std","_Min","_Max"]:
                columnas.append(seleccion + i)
        elif seleccion in unique_columns:
            columnas.append(seleccion)


    Table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in columnas],
        data=dff[time[0]:time[1]].to_dict("rows"),
        page_size=60,
        fixed_rows={'headers': True},
        style_data={'whiteSpace': 'normal','height': 'auto','lineHeight': '20px'},
        style_table={'minWidth': '100%','height': '500px', 'overflowY': 'auto'},
        style_cell={'minWidth': '50px', 'width': '50px', 'maxWidth': '50px','textAlign': 'center'},
        export_format='xlsx',
        export_headers='display',
        editable=True,
        style_data_conditional=[],        
        )
    
    if punto!=None:
        punto = dff[dff['TIMESTAMP'] == punto].index
        punto=str(dff['TIMESTAMP'][punto[0]])
        punto = punto.replace(" ","T")
        Table.style_data_conditional.append({'if': {'filter_query': '{{TIMESTAMP}} = {}'.format(punto)},
                                'backgroundColor': '#FF4136',
                                'color': 'white'})

    return Table

#####################################################################
#                             Llamadas                              #
#####################################################################

#LLamada para obtener las posibles graficas de acuerdo a la categoria seleccionada
@app.callback(
    Output("Posibles_Graficas", "children"),
    Input("Posibles_Categorias", "value")
)
def Selecion_de_graficas(value):

    Opt_Valores = climatic_categories[value]

    if value=="Otros":
        Inicial= Opt_Valores[0]
    else:
        Inicial= Opt_Valores

    valores = dcc.Dropdown(Opt_Valores,
                    Inicial,
                    id="Valores_Graficas",
                    style={'width': '400px'},
                    multi=True,
                    searchable=False,
                    )
    return valores



# Llamada para desactivar deslizante segun contexto
@app.callback(Output('time-range-slider','disabled'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'))
def update_graph(start_date,end_date):
    aux=pd.to_datetime(end_date)-pd.to_datetime(start_date)
    aux=aux.days
 
    if aux==1:
        return False
    else:
        return True
    
#Indicador para grafica
@app.callback(Output('indicator-graphic', 'figure'),
              Input('Valores_Graficas', 'value'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('time-range-slider','value'),
              Input('time-range-slider','disabled'))
def update_graph(Selecciones,Fecha_Inicial,Fecha_Final,Tiempo,Aux):
    Tiempo[0]=int(Tiempo[0])
    Tiempo[1]=int(Tiempo[1])
    largo=650
    if Aux==False:
        fig = grafica(df,Selecciones,Fecha_Inicial,Fecha_Final,Tiempo)
    if Aux==True:
        fig = grafica(df,Selecciones,Fecha_Inicial,Fecha_Final)
    fig.update_layout(margin={'l': 50, 'b': 50, 't': 50, 'r': 50}, 
                        hovermode='x',
                        title=f"BSRN IGEF",
                        clickmode='event+select',
                        autosize=False,
                        width=int(largo*(16/9)),
                        height=largo)
    return fig

#LLamada para mostrar tabla
@app.callback(Output('table-container', 'children'),
              Input('Valores_Graficas', 'value'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('time-range-slider','value'),
              Input('indicator-graphic', 'clickData'))
def update_table(yaxis_column_name,start_date,end_date,time,clickData):
    aux=pd.to_datetime(end_date)-pd.to_datetime(start_date)
    aux=aux.days
    time[0]=int(time[0])
    time[1]=int(time[1])

    if clickData!=None:
        a=json.dumps(clickData, indent=2)
        diccionario = json.loads(a)
        clickData = diccionario["points"][0]["x"]

    if aux==1:
        return Tabla(yaxis_column_name,start_date,end_date,time,punto=clickData)
    else:
        return Tabla(yaxis_column_name,start_date,end_date,punto=clickData)



@app.callback(
    Output('a', 'children'),
    Input('indicator-graphic', 'clickData'),
    State('indicator-graphic',"figure"))
def actualizar_grafica(clickData,figure):
    if clickData!= None:
        print(figure["data"][-1]["selectedpoints"])

    

if __name__ == '__main__':
    app.run_server(debug=True)