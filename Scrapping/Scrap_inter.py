import os
import Tripolis as trip
import Scrap_abandonado as aba
from selenium import webdriver
from collections import Counter
import tkinter as tk
from tkinter import filedialog

"""
Extracción de datos de una apgina web en base a entrada de ususario
"""

## Creamos una clase para la ventana interactiva
class WindowTK():
    def __init__(self):
        # Creating the tkinter Window
        self.root = tk.Tk()
        self.root.title("Entradas de Rutas")
        self.root.geometry("800x300")
        self.root.config(bg="dark gray")
        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_columnconfigure(0, weight = 1)
        
        # Variables
        self.mailpath = None
        self.shoppath = None
        self.clusterpath = None
        self.savefilespath = None
        self.month = None
        self.current_dir = os.getcwd()

        # Creamos label
        l = tk.Label(self.root, text = 'Ingrese el mes en formato MM')
        l.config(font = ("Arial", 9))

        # Input textbox
        self.inputtxt = tk.Text(self.root, height = 1, width = 10)


        # Buttons
        mailButton = tk.Button(self.root, text = "Archivo Mail", command = lambda: self.setPath(1))
        shopButton = tk.Button(self.root,text = "Archivo Ventas", command = lambda: self.setPath(2))
        ClusterButton = tk.Button(self.root, text = 'Archivo Cluster', command = lambda: self.setPath(3))
        pathButton = tk.Button(self.root, text = 'Ruta Descargas', command = self.setFilesPath)
        
        exit_button = tk.Button(self.root, text="Guardar y Salir", command=self.salir)
        
        # Label to display selected path
        self.path_mail = tk.Label(self.root, text="Path: ")
        self.path_shop = tk.Label(self.root, text="Path: ")
        self.path_cluster = tk.Label(self.root, text="Path: ")
        self.path_savefiles = tk.Label(self.root, text="Path: ")


        # Positions
        l.place(x = 10, y = 20)
        mailButton.place(x = 30, y = 80)
        shopButton.place(x = 30, y = 120)
        ClusterButton.place(x = 30, y = 160)
        pathButton.place(x = 30, y = 200)
        

        self.inputtxt.place(x = 200, y = 20)
        self.path_mail.place(x = 140, y = 83)
        self.path_shop.place(x = 140, y = 123)
        self.path_cluster.place(x = 140, y = 163)
        self.path_savefiles.place(x = 140, y = 203)

        exit_button.place(x = 350, y = 255)

        #Call Loop
        self.root.mainloop()

    def salir(self):
        self.month = self.inputtxt.get(1.0, 'end-1c')
        self.root.destroy()
    
    # Files Folder
    # Set Path
    def setFilesPath(self):
        self.savefilespath = filedialog.askdirectory(initialdir=self.current_dir)
        self.path_savefiles.config(text="Path: " + self.savefilespath)

    # Set Path
    def setPath(self, flag):
        ruta = filedialog.askopenfilename(initialdir=self.current_dir, filetypes=[("Excel files","*.xlsx")])

        if flag == 1:
            self.mailpath = ruta
            self.path_mail.config(text="Path: " + ruta)
        elif flag == 2:
            self.shoppath = ruta
            self.path_shop.config(text="Path: " + ruta)
        else:
            self.clusterpath = ruta
            self.path_cluster.config(text="Path: " + ruta)

    # Getters
    def getMailpath(self): 
        return self.mailpath
    def getShoppath(self): 
        return self.shoppath
    def getClusterpath(self): 
        return self.clusterpath
    def getSavePath(self):
        return self.path_savefiles
    def getMonth(self):
        return self.month



def compare(info_path, downloaded_info):
    info_split = [x.split('_')[0] for x in info_path]

    counter = Counter(info_split)

    for element in downloaded_info:
        if counter[element[0]] != element[1]:
            print(f"\nEl número de archivos esperados para {element[0]} es {element[1]}, sin embargo, se recibieron {counter[element[0]]}")
            return 0
    
    return 1

def verify_entries(paths_list, month):
    for i in range(len(paths_list)):
        if paths_list[i][0] == None or paths_list[i][0] == '':
            print(f'La ruta {paths_list[i][1]} fue mal ingresada')
            return 0
    if len(month) != 2 or month < '01' or month > '12':
        print('Fecha en formato incorrecto')
        return 0
    return 1


def main_Tripolis():
    # Show the Window
    w = WindowTK()
    mail = (w.getMailpath(), 'Email')
    shop = (w.getShoppath(), 'Ventas')
    cluster = (w.getClusterpath(), 'Clsuter')
    save = (w.getSavePath(), 'Guardado')
    month = w.getMonth()

    if not verify_entries([mail, shop, cluster, save], month):
        print('\nIngrese los datos nuevamente')
        return

    driver = webdriver.Firefox()

    # Get the returns values
    down_info = trip.main(month, save[0], driver)

    # First: verify that all files are consistent with down_info 
    # and that all of these files have been successfully downloaded

    # Get the list of all files in the directory
    file_names = os.listdir(down_info)

    # Compare info of file_names with down_info
    if not compare(file_names, down_info):
        return

    # Iterate over the file names to know if a file have weight 0
    for file_name in file_names:
        file_path = os.path.join(save[0], file_name)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)

            if int(file_size) == 0:
                print(f'\nEl archivo {file_name} tiene tamaño {file_size} bytes')
                print('verifique la descarga y vuelva a correr el proceso')            
                return 0

    # Next Step: 'Carro Abandonado'
    # we will always have information, and will always have 9 files
    aba.main(save[0], driver)
    

if '__main__' == __name__:
    main_Tripolis()