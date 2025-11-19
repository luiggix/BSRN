import pandas as pd
import numpy as np

# Importamos el DataFrame
df = pd.read_csv("../bsrn/bsrn.csv")

# Conversion de columna 'TIMESTAMP' al formato de fecha de pandas (datatime64)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%Y-%m-%d %H:%M:%S')
start_date = df['TIMESTAMP'][0]
end_date = df['TIMESTAMP'].iloc[-1]

#Conversion de tempartura a Grados Kelvin
df['CRPTemp_Avg']=df['CRPTemp_Avg']+273.15
df['UVTEMP_Avg']=df['UVTEMP_Avg']+273.15
df["DEW_POINT_Avg"] = df["DEW_POINT_Avg"]+273.15

#Agregamos columnas al DataFrame
dif_GH_CALC_GLOBAL=df["GH_CALC_Avg"] - df["GLOBAL_Avg"]
quotient_GH_CALC_GLOBAL=df["GH_CALC_Avg"] / df["GLOBAL_Avg"]
sum_SW = df["DIFFUSE_Avg"] + df["DIRECT_Avg"]*np.cos(np.radians(df["ZenDeg"]))
df["dif_GH_CALC_GLOBAL"]=dif_GH_CALC_GLOBAL
df["quotient_GH_CALC_GLOBAL"]=quotient_GH_CALC_GLOBAL
df["sum_SW"]=sum_SW
df["porcent_2"] = 0.02*sum_SW

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


#Columnas del DataFrame que pertenecen a cada categoría.
basic_parameters = ["GLOBAL","DIRECT","DIFFUSE","GH_CALC_Avg"]
stadistic = ["dif_GH_CALC_GLOBAL","quotient_GH_CALC_GLOBAL","sum_SW"]
shortwave_balance = ["GLOBAL","UPWARD_SW"]
longwave_balance = ["DOWNWARD","UPWARD_LW","DWIRTEMP","UWIRTEMP","CRPTemp_Avg"]
meteorology = ["CRPTemp_Avg","RELATIVE_HUMIDITY_Avg","PRESSURE_Avg","DEW_POINT_Avg"]
ultraviolet = ["UVB","UVTEMP_Avg","UVSIGNAL_Avg"]


categories = [basic_parameters,shortwave_balance,longwave_balance,meteorology,ultraviolet,stadistic]

others = merged_columns.copy()

for j in categories:
    for i in j:
        if i in others:
            others.remove(i)

categories.append(others)


names_categories=["Parametros Basicos","Balance de onda corta","Balance de onda larga","Meteorologia","Ultravioleta","Dispersion","Otros"]

climatic_categories = dict(zip(names_categories,categories))