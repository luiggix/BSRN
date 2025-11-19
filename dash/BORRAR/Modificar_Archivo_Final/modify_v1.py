import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import shutil
import re

def mod_file(path_origin,path_destination):
    """
    Modifica un archivo copiando el contenido desde el archivo de origen al archivo de destino.
    A partir de la línea que contiene "C4000", se reemplazan espacios entre columna 7 a 8 a un solo espacio.

    Int:
    - path_origin (str): Ruta del archivo de origen.
    - path_destination (str): Ruta del archivo de destino.

    """
    #Copiamos el archivo:
    shutil.copy(path_origin, path_destination)   

    #Variables auxiliares
    modify=False
    content=[]
    count=0
    #Leemos el documento
    with open(path_destination) as archive:
        lines = archive.readlines()
        for line in  lines:
            #Modificamos el contenido
            if modify:
                cadena = re.split(r"(\s+)", line)
                #Modificacion entre cadena 2 y 3
                cadena[5]=" "
                #Modificacion entre cadena 7 y 8
                cadena[15]=" "
                
                #condiciones para modificar columna 11 y 12
                if len(cadena[24])==3:
                    cadena[23]="   "
                if len(cadena[24])==4:
                    cadena[23]="  "
                elif len(cadena[24])==5:
                    cadena[23]=" "
                    
                line="".join(cadena)

            content.append(line)

            if "C4000" in line:
                modify=True
                continue

    #Reescribimos el documento
    with open(path_destination, 'w') as archive:
        archive.writelines(content)      
    



root = tk.Tk()

#Creamos un boton para buscar la carpeta con los archivos
button1 = tk.Button(root, text="Seleccionar archivo", command=lambda:select_file())
button1.grid(row=1)

button2 = tk.Button(root, text="Seleccionar carpeta de destino", command=lambda:select_path(),state=tk.DISABLED)
button2.grid(row=2)

label = tk.Label(root, text="Ingrese el nombre del archivo:")
label.grid(row=3)

entry = tk.Entry(root)
entry.grid(row=4)

button3 = tk.Button(root, text="Modificar", command=lambda:modify(),state=tk.DISABLED)
button3.grid(row=5)

#Define una función para abrir el diálogo de selección de carpeta
def select_file():
    global path_origin
    origin=filedialog.askopenfile()
    path_origin = origin.name
    button2.configure(state=tk.ACTIVE)
    button1.configure(state=tk.DISABLED)
    print(path_origin)

def select_path():
    global path_destination
    path_destination=filedialog.askdirectory()
    button2.configure(state=tk.DISABLED)
    button3.configure(state=tk.ACTIVE)
    print(path_destination)

def modify():
    texto = entry.get()
    if texto=="":
        messagebox.showinfo("Nombre no ingresado", "Ingresa un nombre para el archivo destino")
        pass
    else:
        mod_file(path_origin,path_destination+"/"+texto+".dat")
        root.destroy()
    
    
root.mainloop()        