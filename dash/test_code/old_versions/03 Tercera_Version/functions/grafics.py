import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np 
from functions.columns import *
from scipy.stats import linregress

def make_graphic(selections,start,end,time=[0,-1]):

    """
    Función que genera gráficos con datos climáticos filtrados.

    Args:
        selections (list): 
            Variable(s) a graficar.
        start (str):       
            Fecha inicial de los datos a graficar en formato "YYYY-MM-DD".
        end (str):         
            Fecha final de los datos a graficar en formato "YYYY-MM-DD".
        time (list):       
            Hora de inicio y fin en formato "HH:MM:SS" para los datos a graficar. 
            Por defecto, se grafica el día completo.

    Returns:
        fig (objeto plotly): 
            Figura con la(s) gráfica(s) generada(s).
    """
    initial = df[df['TIMESTAMP'] == start].index
    final   = df[df['TIMESTAMP'] == end].index
    dff=df[initial [0]:final[0]]

    
       #Filtros para cada variable

    #Filtros para angulo cenital menor a 90 y mayor a cero
    zen_filter = (dff["ZenDeg"]>=0) & (dff["ZenDeg"]<=90)
    filtered_dff = dff.loc[zen_filter]

    #Variables para filtros
    var_AU = 1
    var_sa = 1366/(var_AU**2)
    var_mu0 = np.cos(np.radians(filtered_dff["ZenDeg"]))

    #Filtro para varible global
    filter_rare_limits_global = var_sa*1.2*var_mu0**(1.2)+50
    global_filter = (filtered_dff["GLOBAL_Avg"]>=-2 ) & (filter_rare_limits_global>=filtered_dff["GLOBAL_Avg"]) 
    filtered_global_rare_limits = filtered_dff.loc[global_filter]
    merged = pd.merge(filtered_dff, filtered_global_rare_limits, how='left', indicator=True)
    filtered_global_normal = merged.loc[merged['_merge'] == 'left_only']


    #Filtro para varible Difussa
    filter_rare_limits_diffuse = var_sa*0.95*var_mu0**(1.2)+10
    diffuse_filter = (filter_rare_limits_diffuse>=filtered_dff["DIFFUSE_Avg"]) & (filtered_dff["DIFFUSE_Avg"]>=-2 )
    filtered_diffuse_rare_limits = filtered_dff.loc[diffuse_filter]
    merged = pd.merge(filtered_dff, filtered_diffuse_rare_limits, how='left', indicator=True)
    filtered_diffuse_normal = merged.loc[merged['_merge'] == 'left_only']
    

    #Filtro para varible Directa
    filter_rare_limits_direct = var_sa*0.95*var_mu0**(0.2)+10
    direct_filter = (filter_rare_limits_direct>=filtered_dff["DIRECT_Avg"]) & (filtered_dff["DIRECT_Avg"]>=-2 )
    filtered_direct_rare_limits = filtered_dff.loc[direct_filter]
    merged = pd.merge(filtered_dff, filtered_direct_rare_limits, how='left', indicator=True)
    filtered_direct_normal = merged.loc[merged['_merge'] == 'left_only']
    

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

    elif selections[-1] in stadistic:
        fig = make_subplots(rows=3, cols=1)
        row_=1
        col_=1
        aux1=5

    for selection in selections:

        #Opciones datos basicos
        if(aux1==0):
            if selections[-1] in basic_parameters:
                fig.update_layout(title="BSRN IGEF, Parametros Basicos")
            elif selections[-1] in shortwave_balance:
                fig.update_layout(title="BSRN IGEF, Balance de onda Corta")
            fig.update_xaxes(title_text="Día, Hora", row=1, col=1)
            fig.update_yaxes(title_text="W/m^2", row=1, col=1)

        #Opciones para Balance_de_onda_larga
        if (aux1==1):
            fig.update_layout(title="BSRN IGEF, Balance de onda larga")
            fig.update_yaxes(title_text="Temp", row=2, col=1)
            fig.update_yaxes(title_text="W/m^2", row=1, col=1)
            fig.update_xaxes(title_text="Dia, Hora", row=2, col=1)

            if  (selection in ([longwave_balance[0]] +[longwave_balance[1]])):
                row_=1
            else:
                row_=2

        #Opciones para Meteorologia
        if (aux1==2):
            fig.update_layout(title="BSRN IGEF, Balance de onda larga")
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
            fig.update_layout(title="BSRN IGEF, Metrologia")
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
            fig.update_layout(title="BSRN IGEF, Otros")
            fig.update_yaxes(title_text=" ", row=1, col=1)
            fig.update_xaxes(title_text=" ", row=1, col=1)

        #Opciones para Estadisticas
        if (aux1==5):
            fig.update_layout(title="BSRN IGEF, Est")
            fig.update_xaxes(title_text="", row=1, col=1)
            fig.update_yaxes(title_text="W/m^2", row=1, col=1)
            fig.update_yaxes(title_text="W/m^2", row=2, col=1)

            fig.update_xaxes(title_text="Día, Hora", row=3, col=1)
            fig.update_yaxes(title_text="", row=3, col=1)

            if selection == "dif_GH_CALC_GLOBAL":
                row_=1
                col_=1
            elif selection == "quotient_GH_CALC_GLOBAL":
                row_=3
                col_=1
            elif selection == "sum_SW":
                row_=2
                col_=1


        if selection in common_list:
                
            Avg = selection + "_Avg"
            Std = selection + "_Std"
            Min = selection + "_Min"
            Max = selection + "_Max"    

            var = ["GLOBAL", "DIFFUSE","DIRECT"]

            if selection not in var :
                x_1 = filtered_global_rare_limits["TIMESTAMP"][time[0]:time[1]]
                y_1 = filtered_dff[Avg][time[0]:time[1]]

            elif selection == "GLOBAL":
                x_2 = filtered_global_normal["TIMESTAMP"][time[0]:time[1]]
                y_2 = filtered_global_normal[Avg][time[0]:time[1]]
                x_1 = filtered_global_rare_limits["TIMESTAMP"][time[0]:time[1]]
                y_1 = filtered_global_rare_limits[Avg][time[0]:time[1]]
                
            elif selection == "DIFFUSE":
                x_2 = filtered_diffuse_normal["TIMESTAMP"][time[0]:time[1]]
                y_2 = filtered_diffuse_normal[Avg][time[0]:time[1]]
                x_1 = filtered_diffuse_rare_limits["TIMESTAMP"][time[0]:time[1]]
                y_1 = filtered_diffuse_rare_limits[Avg][time[0]:time[1]]
                
            elif selection == "DIRECT":
                x_2 = filtered_direct_normal["TIMESTAMP"][time[0]:time[1]]
                y_2 = filtered_direct_normal[Avg][time[0]:time[1]]
                x_1 = filtered_direct_rare_limits["TIMESTAMP"][time[0]:time[1]]
                y_1 = filtered_direct_rare_limits[Avg][time[0]:time[1]]
                
            
            fig.add_trace(go.Scatter(x = x_1, 
                                y = y_1,
                                error_y = dict(type='data',array=filtered_dff[Std][time[0]:time[1]], visible=True,width=1),
                                mode = 'lines',
                                line=dict(width=1),
                                connectgaps=False,
                                name = Avg.replace("_"," ")),
                                row=row_,col=col_)
            
            if selection in var:
                fig.add_trace(go.Scatter(x = x_2, 
                                    y = y_2,
                                    error_y = dict(type='data',array=filtered_dff[Std][time[0]:time[1]], visible=True,width=1),
                                    mode = 'markers',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = "Extremely rare limits "+Avg.replace("_"," ")),
                                    row=row_,col=col_)

            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_dff[Min][time[0]:time[1]],
                                    mode = 'lines',
                                    line=dict(width=1),
                                    name = Min.replace("_"," "),
                                    connectgaps=False,
                                    visible = "legendonly"),
                                    row=row_,col=col_)
            
            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_dff[Max][time[0]:time[1]],
                                    mode = 'lines',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = Max.replace("_"," "),
                                    visible = "legendonly"),
                                    row=row_,col=col_)
            if (selection in var) and (selection != "GLOBAL"):
                fig.update_traces(visible = "legendonly",selector=dict(name=Avg.replace("_"," ")))
                fig.update_traces(visible = "legendonly",selector=dict(name="Extremely rare limits "+Avg.replace("_"," ")))

        elif selection in unique_columns:
            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"][time[0]:time[1]], 
                                    y = filtered_dff[selection][time[0]:time[1]],
                                    mode = 'lines',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = str(selection).replace("_"," ")),
                                    row=row_,col=col_)
            if selection == "sum_SW":
                x = filtered_dff["GLOBAL_Avg"][time[0]:time[1]]
                y = filtered_dff[selection][time[0]:time[1]]

                slope, intercept, r_value, p_value, std_err = linregress(x,y)
                x_trend = np.linspace(min(x), max(x), 100)
                y_trend = slope * x_trend + intercept

                fig.update_traces(x = filtered_dff["GLOBAL_Avg"][time[0]:time[1]],
                                  error_y = dict(type='data',array=filtered_dff["porcent_2"][time[0]:time[1]], visible=True,width=1),
                                  mode="markers",
                                  marker=dict(size=3),
                                  row=row_,
                                  col=col_)
                fig.add_trace(go.Scatter(x=x_trend, y=y_trend, mode='lines', 
                             name='Línea de tendencia, Pendiente = ' + str(np.around(slope,2))),row=row_,col=col_)
        
    return fig
