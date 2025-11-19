import json
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from dash import dash_table

# Importamos el DataFrame
df = pd.read_csv("bsrn/bsrn.csv")

# Conversion de columna 'TIMESTAMP' al formato de fecha de pandas (datatime64)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%Y-%m-%d %H:%M:%S')
start_date = df['TIMESTAMP'][0]
end_date = df['TIMESTAMP'].iloc[-1]

# Guardamos todas las culumnas del DataFrame
Columnas=[]
for i in df.columns:
    Columnas.append(i)

# Columnas provicionales para trabajar
Avg_list = [x.replace("_Avg","") for x in Columnas if x.endswith("Avg")]
Std_list = [x.replace("_Std","") for x in Columnas if x.endswith("Std")]
Min_list = [x.replace("_Min","") for x in Columnas if x.endswith("Min")]
Max_list = [x.replace("_Max","") for x in Columnas if x.endswith("Max")]

Elementos_comunes = list(set(Avg_list) & set(Std_list) & set(Min_list) & set(Max_list))

aux = [elemento + "_" + str(i) for elemento in Elementos_comunes for i in ["Avg","Std","Min","Max"]]
Columnas_unicas=Columnas.copy()
for i in aux:
    Columnas_unicas.remove(i)

Columnas_unicas.remove("TIMESTAMP")
Columnas_unicas.remove("RECORD")

Columnas_totales = Columnas_unicas+Elementos_comunes
#Ordenamos en orden alfabetico Ascendente
Columnas_totales.sort()

app = Dash(__name__)

# Grafica a Mostrar
Opciones_iniciales = dcc.Dropdown(Columnas_totales,
                    'GLOBAL',
                    id="yaxis-column_1",
                    style={'width': '400px'},
                    multi=True
                    )



# Rango de Fechas
Rang_Date = dcc.DatePickerRange(id='my-date-picker-range',
                                min_date_allowed=df['TIMESTAMP'][0],
                                max_date_allowed=df['TIMESTAMP'].iloc[-1],
                                initial_visible_month=df['TIMESTAMP'][0],
                                start_date=df['TIMESTAMP'][0],
                                end_date=df['TIMESTAMP'][1440]) 

#Rango de Tiempo
Rang_Time = dcc.RangeSlider(
        id='time-range-slider',
        min=0,
        max=1440,
        value=[0,1440],
        marks={i*60: "{}:00".format(i) for i in range(25)}
    )



app.layout = html.Div([
    html.H1("BSRN IGEF"),

    html.Hr(),

    html.Div([html.H3("Seleccione los datos a graficar"),Opciones_iniciales],
              style={'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),

    html.Hr(),

    html.Div(id='options'),

    html.Hr(),

    html.Div([html.H3("Seleccione el perido de fechas deseado"),Rang_Date],
              style={'display': 'flex', 'flex-direction': 'column',"height":'100px',"text-align": "center","align-items": "center"}),
    
    html.Br(),
    html.Hr(),
    
    html.H3("Seleccione el perido de tiempo deseado (Al seleccionar mas de un dia en la opción anterior, esta se desactiva)"),
    Rang_Time,

    html.Hr(),

    
    dcc.Graph(id='indicator-graphic'),

    html.Hr(),

    html.Br(),
    html.H3("Datos totales"),
    html.Div(id='table-container')

],style={"text-align": "center","align-items": "center"})


#Tabla 
def Tabla(selecciones,start,end,time=[0,-1],punto=None):

    columnas=["TIMESTAMP"]

    inicial = df[df['TIMESTAMP'] == start].index
    final   = df[df['TIMESTAMP'] == end].index
    dff=df[inicial[0]:final[0]]

    if type(selecciones) != list:
            selecciones=[selecciones]

    for seleccion in selecciones:
        if seleccion in Elementos_comunes:
            for i in ["_Avg","_Std","_Min","_Max"]:
                columnas.append(seleccion + i)
        elif seleccion in Columnas_unicas:
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




def grafica(selecciones,start,end,time=[0,-1]):
    #Función para graficar 
    
    inicial = df[df['TIMESTAMP'] == start].index
    final   = df[df['TIMESTAMP'] == end].index
    dff=df[inicial[0]:final[0]]
    
    fig = go.Figure()
    
    if type(selecciones) != list:
            selecciones=[selecciones]
    
    for seleccion in selecciones:
        if seleccion in Elementos_comunes:

            Avg = seleccion + "_Avg"
            Std = seleccion + "_Std"
            Min = seleccion + "_Min"
            Max = seleccion + "_Max"    


            fig.add_trace(go.Scatter(x = dff["TIMESTAMP"][time[0]:time[1]], 
                                     y = dff[Avg][time[0]:time[1]],
                                     error_y = dict(type='data',array=dff[Std][time[0]:time[1]], visible=True),
                                     mode = 'markers',
                                     name = Avg))
            fig.add_trace(go.Scatter(x = dff["TIMESTAMP"][time[0]:time[1]], 
                                     y = dff[Min][time[0]:time[1]],
                                     mode = 'lines',
                                     name = Min,
                                     visible = "legendonly"))
            fig.add_trace(go.Scatter(x = dff["TIMESTAMP"][time[0]:time[1]], 
                                     y = dff[Max][time[0]:time[1]],
                                     mode = 'lines',
                                     name = Max,
                                     visible = "legendonly"))
        elif seleccion in Columnas_unicas:
            fig.add_trace(go.Scatter(x = dff["TIMESTAMP"][time[0]:time[1]], 
                                     y = dff[seleccion][time[0]:time[1]],
                                     mode = 'markers',
                                     name = str(seleccion)))

    return fig




#Indicador para grafica
@app.callback(Output('indicator-graphic', 'figure'),
              Output('time-range-slider','disabled'),
              Input('yaxis-column_1', 'value'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('time-range-slider','value'))
def update_graph(yaxis_column_name,start_date,end_date,time):
    aux=pd.to_datetime(end_date)-pd.to_datetime(start_date)
    aux=aux.days

    time[0]=int(time[0])
    time[1]=int(time[1])    
    if aux==1:
        fig = grafica(yaxis_column_name,start_date,end_date,time)
        fig.update_layout(margin={'l': 50, 'b': 50, 't': 50, 'r': 50}, 
                          hovermode='closest',
                          title=f"BSRN IGEF {yaxis_column_name}",
                          xaxis_title="Día, Hora",
                          yaxis_title="SWD [W/m2]",
                          clickmode='event+select')
        return fig,False
    else:
        fig = grafica(yaxis_column_name,start_date,end_date)
        fig.update_layout(margin={'l': 50, 'b': 50, 't': 50, 'r': 50}, 
                          hovermode='closest',
                          title=f"BSRN IGEF {yaxis_column_name}",
                          xaxis_title="Día, Hora",
                          yaxis_title="SWD [W/m2]",
                          clickmode='event+select')
        return fig,True

#Indicador para tabla
@app.callback(Output('table-container', 'children'),
              Input('yaxis-column_1', 'value'),
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



if __name__ == '__main__':
    app.run_server(debug=True)