import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np 
from functions.columns import *
from scipy.stats import linregress
from functions.options import *


def filtered(df,variable,product,power,bias):
    #Variables necesarias
    var_AU = 1
    var_sa = 1366/(var_AU**2)
    var_mu0 = np.cos(np.radians(df["ZenDeg"]))

    #Filtro para varible
    filter_rare_limits = var_sa*product*var_mu0**(power)+bias
    variable_filter_limits = (df[variable]>=-2 ) & (filter_rare_limits>=df[variable]) 
    df_filtered_normal = df.loc[variable_filter_limits]
    merged = pd.merge(df, df_filtered_normal, how='left', indicator=True)
    df_filtered_limits = merged.loc[merged['_merge'] == 'left_only']
    
    return df_filtered_normal,df_filtered_limits

def make_graphic(categorie,selections,start,end):

    """
    Función que genera gráficos con datos climáticos filtrados.

    Args:
        categorie (str):
            Categoria seleccionada
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

    if type(selections) != list:
        selections=[selections]

    title_subplot = "BSRN IGEF, "
       #Filtros para cada variable

    #Filtros para angulo cenital menor a 90 y mayor a cero
    zen_filter = (dff["ZenDeg"]>=0) & (dff["ZenDeg"]<=90)
    filtered_dff = dff.loc[zen_filter]

        #Definimos el tipo de figura de acuerdo con las graficas
    #Usamos comprension de diccionarios para hallar a que categoria corresponde las graficas seleccionadas
    option_ = options_type.get(categorie)[0]
    row_ =  options_type.get(categorie)[1]
    col_ =  options_type.get(categorie)[2]

    #Creamos el objeto para los subplots
    fig = make_subplots(rows=row_,cols=col_)
    fig.update_layout(title=title_subplot + categorie)

    #Seleccionamos las opciones de acuerdo a la categoria 
    axes_options=list(zip([u for u in options_type.get(categorie)[3]],
                      [v for v in options_type.get(categorie)[4]],
                      [(x, y) for x in range(1, row_+1) for y in range(1, col_+1)]))
    
    for axe_options in axes_options:
        fig.update_xaxes(title_text = axe_options[0], row = axe_options[-1][0],col = axe_options[-1][1])
        fig.update_yaxes(title_text = axe_options[1], row = axe_options[-1][0],col = axe_options[-1][1])

    for selection in selections:    

        #Opciones para Balance_de_onda_larga
        if (option_==3):
            if  (selection in ([longwave_balance[0]] +[longwave_balance[1]])):
                row_=1
            else:
                row_=2

        #Opciones para Meteorologia
        if (option_==4):
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
        if (option_==5):
            if selection == "UVB":
                row_=1
                col_=1
            elif selection == "UVTEMP_Avg":
                row_=2
                col_=1
            elif selection == "UVSIGNAL_Avg":
                row_=3
                col_=1

    
        #Opciones para Estadisticas
        if (option_==6):

            if selection == "dif_GH_CALC_GLOBAL":
                row_=1
                col_=1
            elif selection == "ratio_GH_CALC_GLOBAL":
                row_=2
                col_=1
            elif selection == "sum_SW":
                row_=3
                col_=1


        if selection in common_list:
                
            Avg = selection + "_Avg"
            Std = selection + "_Std"
            Min = selection + "_Min"
            Max = selection + "_Max"    

            var = ["GLOBAL", "DIFFUSE","DIRECT"]

            if selection not in var :
                x_1 = filtered_dff["TIMESTAMP"] 
                y_1 = filtered_dff[Avg] 

            elif selection == "GLOBAL":
                #Filtro para varible global
                filtered_global_normal,filtered_global_rare_limits = filtered(filtered_dff,*filter_type.get("GLOBAL"))
                x_1 = filtered_global_normal["TIMESTAMP"] 
                y_1 = filtered_global_normal[Avg] 
                x_2 = filtered_global_rare_limits["TIMESTAMP"] 
                y_2 = filtered_global_rare_limits[Avg] 
                
            elif selection == "DIFFUSE":
                #Filtro para varible Difussa
                filtered_diffuse_normal,filtered_diffuse_rare_limits=filtered(filtered_dff,*filter_type.get("DIFFUSE"))
                x_1 = filtered_diffuse_normal["TIMESTAMP"] 
                y_1 = filtered_diffuse_normal[Avg] 
                x_2 = filtered_diffuse_rare_limits["TIMESTAMP"] 
                y_2 = filtered_diffuse_rare_limits[Avg] 
                
            elif selection == "DIRECT":
                #Filtro para varible Directa
                filtered_direct_normal,filtered_direct_rare_limits=filtered(filtered_dff,*filter_type.get("DIRECT"))
                x_1 = filtered_direct_normal["TIMESTAMP"] 
                y_1 = filtered_direct_normal[Avg] 
                x_2 = filtered_direct_rare_limits["TIMESTAMP"] 
                y_2 = filtered_direct_rare_limits[Avg] 
                
            
            fig.add_trace(go.Scatter(x = x_1, 
                                y = y_1,
                                error_y = dict(type='data',array=filtered_dff[Std] , visible=True,width=1),
                                mode = 'lines',
                                line=dict(width=1),
                                connectgaps=False,
                                name = Avg.replace("_"," ")),
                                row=row_,col=col_)
            
            if selection in var:
                fig.add_trace(go.Scatter(x = x_2, 
                                    y = y_2,
                                    error_y = dict(type='data',array=filtered_dff[Std] , visible=True,width=1),
                                    mode = 'markers',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = "Extremely rare limits "+Avg.replace("_"," ")),
                                    row=row_,col=col_)

            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"] , 
                                    y = filtered_dff[Min] ,
                                    mode = 'lines',
                                    line=dict(width=1),
                                    name = Min.replace("_"," "),
                                    connectgaps=False,
                                    visible = "legendonly"),
                                    row=row_,col=col_)
            
            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"] , 
                                    y = filtered_dff[Max] ,
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
            fig.add_trace(go.Scatter(x = filtered_dff["TIMESTAMP"] , 
                                    y = filtered_dff[selection] ,
                                    mode = 'lines',
                                    line=dict(width=1),
                                    connectgaps=False,
                                    name = str(selection).replace("_"," ")),
                                    row=row_,col=col_)
            if selection == "sum_SW":
                x = filtered_dff["GLOBAL_Avg"] 
                y = filtered_dff[selection] 

                slope, intercept, r_value, p_value, std_err = linregress(x,y)
                x_trend = np.linspace(min(x), max(x), 100)
                y_trend = slope * x_trend + intercept

                fig.update_traces(x = filtered_dff["GLOBAL_Avg"] ,
                                  error_y = dict(type='data',array=filtered_dff["porcent_2"] , visible=True,width=1),
                                  mode="markers",
                                  marker=dict(size=3),
                                  name = "Dispersion",
                                  row=row_,
                                  col=col_)
                fig.add_trace(go.Scatter(x=x_trend, y=y_trend, mode='lines', 
                             name='Línea de tendencia, Pendiente = ' + str(np.around(slope,2))),row=row_,col=col_)
        
    return fig
