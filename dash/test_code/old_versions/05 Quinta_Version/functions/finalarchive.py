import pandas as pd
from functions.columns import *

options=dict(C0100=["GLOBAL_Avg",
                    "GLOBAL_Std",
                    "GLOBAL_Min",
                    "GLOBAL_Max",
                    "DIRECT_Avg",
                    "DIRECT_Std",
                    "DIRECT_Min",
                    "DIRECT_Max",
                    "DIFFUSE_Avg",
                    "DIFFUSE_Std",
                    "DIFFUSE_Min",
                    "DIFFUSE_Max",
                    "DOWNWARD_Avg",
                    "DOWNWARD_Std",
                    "DOWNWARD_Min",
                    "DOWNWARD_Max",
                    "AIR_TEMPERATURE_Avg",
                    "RELATIVE_HUMIDITY_Avg",
                    "PRESSURE_Avg","empy"],
             C0200=["GLOBAL_Avg",
                    "GLOBAL_Std",
                    "GLOBAL_Min",
                    "GLOBAL_Max"],
             C0300=["UPWARD_SW_Avg",
                    "UPWARD_SW_Std",
                    "UPWARD_SW_Min",
                    "UPWARD_SW_Max",
                    "UPWARD_LW_Avg",
                    "UPWARD_LW_Std",
                    "UPWARD_LW_Min",
                    "UPWARD_LW_Max",
                    "UVB_Avg",
                    "UVB_Std",
                    "UVB_Min",
                    "UVB_Max"],
             C0500=["UVB_Avg",
                    "UVB_Std",
                    "UVB_Min",
                    "UVB_Max"],
             C4000=["DWIRTEMP_Avg",
                    "DWIRTEMP_Std",
                    "DWIRTEMP_Min",
                    "DWIRTEMP_Max",
                    "DOWNWARD_Avg",
                    "UWIRTEMP_Avg",
                    "UWIRTEMP_Std",
                    "UWIRTEMP_Min",
                    "UWIRTEMP_Max",
                    "UPWARD_LW_Avg"])

def generate(mes):
    path_origin=r"..\bsrn\fijo.dat"
    path_destination="Final.dat"

    day = [x.day for x in df["TIMESTAMP"]]
    minute = [x.hour*60+x.minute for x in df["TIMESTAMP"]]
    month = [x.month for x in df["TIMESTAMP"]]

    with open(path_origin) as archive:
        lines = archive.readlines()    
        
    lines.append("\n")
    for i in options.keys():
        
        lines.append("*"+i+"\n")
        print(i)

        dff=df[list(options[i])]
        dff.insert(0,"minute",minute)
        dff.insert(0,"day",day)
        dff=dff[0:month.index(5)-1]
        
        
        try:
            dff["GLOBAL_Avg"]=dff["GLOBAL_Avg"].astype(int)
            dff["GLOBAL_Std"]=dff["GLOBAL_Std"].round(1)
            dff["GLOBAL_Min"]=dff["GLOBAL_Min"].astype(int)
            dff["GLOBAL_Max"]=dff["GLOBAL_Max"].astype(int)
        except:
            pass

        try:
            dff["DIRECT_Avg"]=dff["DIRECT_Avg"].astype(int)
            dff["DIRECT_Std"]=dff["DIRECT_Std"].round(1)
            dff["DIRECT_Min"]=dff["DIRECT_Min"].astype(int)
            dff["DIRECT_Max"]=dff["DIRECT_Max"].astype(int)
        except:
            pass

        try:
            dff["DIFFUSE_Avg"]=dff["DIFFUSE_Avg"].astype(int)
            dff["DIFFUSE_Std"]=dff["DIFFUSE_Std"].round(1)
            dff["DIFFUSE_Min"]=dff["DIFFUSE_Min"].astype(int)
            dff["DIFFUSE_Max"]=dff["DIFFUSE_Max"].astype(int)
        except:
            pass
        
        try:
            dff["DOWNWARD_Avg"]=dff["DOWNWARD_Avg"].astype(int)
            dff["DOWNWARD_Std"]=dff["DOWNWARD_Std"].round(1)
            dff["DOWNWARD_Min"]=dff["DOWNWARD_Min"].astype(int)
            dff["DOWNWARD_Max"]=dff["DOWNWARD_Max"].astype(int)
        except:
            pass
            
        try:
            dff["UPWARD_SW_Avg"]=dff["UPWARD_SW_Avg"].astype(int)
            dff["UPWARD_SW_Std"]=dff["UPWARD_SW_Std"].round(1)
            dff["UPWARD_SW_Min"]=dff["UPWARD_SW_Min"].astype(int)
            dff["UPWARD_SW_Max"]=dff["UPWARD_SW_Max"].astype(int)
        except:
            pass
            
        
        
        try:
            dff["UPWARD_LW_Avg"]=dff["UPWARD_LW_Avg"].astype(int)
            dff["UPWARD_LW_Std"]=dff["UPWARD_LW_Std"].round(1)
            dff["UPWARD_LW_Min"]=dff["UPWARD_LW_Min"].astype(int)
            dff["UPWARD_LW_Max"]=dff["UPWARD_LW_Max"].astype(int)
        except:
            pass
        
        
        
        try:    
            dff["DWIRTEMP_Avg"]=dff["DWIRTEMP_Avg"].round(2)
            dff["DWIRTEMP_Std"]=dff["DWIRTEMP_Std"].round(2)
            dff["DWIRTEMP_Min"]=dff["DWIRTEMP_Min"].round(2)
            dff["DWIRTEMP_Max"]=dff["DWIRTEMP_Max"].round(2)
        except:
            pass
            
        
        try:
            dff["UWIRTEMP_Avg"]=dff["UWIRTEMP_Avg"].round(2)
            dff["UWIRTEMP_Std"]=dff["UWIRTEMP_Std"].round(2)
            dff["UWIRTEMP_Min"]=dff["UWIRTEMP_Min"].round(2)
            dff["UWIRTEMP_Max"]=dff["UWIRTEMP_Max"].round(2)
        except:
            pass    
        
        if i=="C0500" or i =="C0300":
            dff["UVB_Avg"] = df["UVB_Avg"].fillna(-999)
            dff["UVB_Std"] = df["UVB_Std"].fillna(-99.9)
            dff["UVB_Min"] = df["UVB_Min"].fillna(-999)
            dff["UVB_Max"] = df["UVB_Max"].fillna(-999)

            dff["UVB_Avg"]=dff["UVB_Avg"].round(2)
            dff["UVB_Std"]=dff["UVB_Std"].round(2)
            dff["UVB_Min"]=dff["UVB_Min"].round(2)
            dff["UVB_Max"]=dff["UVB_Max"].round(2)
            
        if i=="C4000":
            dff["UWIRTEMP_Max"] = df["UWIRTEMP_Max"].fillna(-999)
            
        if i=="C0100":
            try:
                dff["AIR_TEMPERATURE_Avg"] = df["AIR_TEMPERATURE_Avg"].fillna(-99.9)
                dff["RELATIVE_HUMIDITY_Avg"] = df["RELATIVE_HUMIDITY_Avg"].fillna(-99.9)
                dff["PRESSURE_Avg"] = df["PRESSURE_Avg"].fillna(-999)

                dff["AIR_TEMPERATURE_Avg"]=dff["AIR_TEMPERATURE_Avg"].round(1)
                dff["RELATIVE_HUMIDITY_Avg"]=dff["RELATIVE_HUMIDITY_Avg"].round(1)
                dff["PRESSURE_Avg"]=dff["PRESSURE_Avg"].astype(int)
            except:
                pass
        
            columnas_1=["day","minute","GLOBAL_Avg","GLOBAL_Std","GLOBAL_Min","GLOBAL_Max","DIRECT_Avg","DIRECT_Std","DIRECT_Min",
                        "DIRECT_Max","empy","empy","empy"]

            columnas_2=["empy","empy","DIFFUSE_Avg","DIFFUSE_Std","DIFFUSE_Min","DIFFUSE_Max","DOWNWARD_Avg","DOWNWARD_Std",
                        "DOWNWARD_Min","DOWNWARD_Max","AIR_TEMPERATURE_Avg","RELATIVE_HUMIDITY_Avg","PRESSURE_Avg"]
            
            dff1=dff[columnas_1]
            dff2=dff[columnas_2]
            dff3=pd.DataFrame(columns=columnas_1)
            
            ultimo_indice=0
            for i in range(0,1440):
                dff3.loc[ultimo_indice+1] = dff1.iloc[i].tolist()
                ultimo_indice = dff3.index[-1]
                dff3.loc[ultimo_indice+1] = dff2.iloc[i].tolist()
                ultimo_indice = dff3.index[-1]
            
            cadena = dff3[0:1440*2].to_string(col_space=0,header=False,index=False) + "\n"
        
        else:
            cadena = dff[0:1440].to_string(col_space=0,header=False,index=False) + "\n"
        
        lines.append(cadena)
        
    with open(path_destination, 'w',newline='') as archive:
        archive.writelines(lines)   