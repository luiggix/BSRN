import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, time



# Definir la ruta del archivo CSV
file_path = "../data/BSRN_2023_01_ene.csv"

# Leer datos desde el archivo CSV y convertir TIMESTAMP a datetime
data = pd.read_csv(file_path)
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
    

