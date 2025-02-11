'''
Code to Download the archives of Tripolis.
'''
import os
import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import tkinter as tk
from tkinter import filedialog
import datetime
import ctypes
import logging

# global parameters
global SAVE_PATH
global DOWNLOAD_PATH
global FILE_PATH


def write_to_log(message, log_level='INFO'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'[{timestamp}] [{log_level}] {message}\n'
    
    with open(FILE_PATH, 'a') as log_file:
        log_file.write(log_entry)

def set_file_readonly(file_path_):
    FILE_ATTRIBUTE_READONLY = 0x00000001
    ret = ctypes.windll.kernel32.SetFileAttributesW(file_path_, FILE_ATTRIBUTE_READONLY)
    return ret != 0

def close_log():
    ## Setting in read-only
    # Set the log file to be read-only
    if set_file_readonly(FILE_PATH):
        print(f"El archivo '{FILE_PATH}' fue dejado como solo lectura")
    else:
        print(f"No se pudo dejar el archivo'{FILE_PATH}'como solo lectura") 

## Creamos una clase para la ventana interactiva
class WindowTK():
    def __init__(self):
        # Creating the tkinter Window
        self.root = tk.Tk()
        self.root.title("Descarga de archivos '__'")
        self.root.geometry("800x300")
        self.root.config(bg="dark gray")
        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_columnconfigure(0, weight = 1)
        
        # Variables
        self.mailpath = None
        self.savefilespath = None
        self.downloadfilespath = None
        self.month = None
        self.password = None
        self.current_dir = os.getcwd()

        # Creamos label
        l = tk.Label(self.root, text = 'Ingrese el número del mes en formato MM')
        l.config(font = ("Arial", 9))

        l_correo = tk.Label(self.root, text = 'Ingrese su correo')
        l_correo.config(font = ("Arial", 9))

        l_pass = tk.Label(self.root, text = 'Ingrese su contraseña')
        l_pass.config(font = ("Arial", 9))

        # Input textbox
        self.inputtxt = tk.Text(self.root, height = 1, width = 10)
        self.inputmail = tk.Text(self.root, height = 1, width = 50)
        self.inputpass = tk.Text(self.root, height = 1, width = 50)

        # Buttons
        pathButton = tk.Button(self.root, text = 'Ruta Guardado', command = self.setFilesPath)
        pathdownloadButton = tk.Button(self.root, text = 'Ruta Descarga', command = self.setFilesPath2)
        
        exit_button = tk.Button(self.root, text="Guardar y Salir", command=self.salir)
        
        # Label to display selected path
        self.path_savefiles = tk.Label(self.root, text="Path: ")
        self.path_downloadfiles = tk.Label(self.root, text="Path: ")

        # Positions
        l.place(x = 10, y = 20)
        self.inputtxt.place(x = 270, y = 20)

        l_correo.place(x = 10, y = 65)
        self.inputmail.place(x = 140, y = 65)

        l_pass.place(x=10, y = 105)
        self.inputpass.place(x = 160, y = 105)

        pathButton.place(x = 30, y = 150)
        self.path_savefiles.place(x = 140, y = 150)

        pathdownloadButton.place(x = 30, y = 195)
        self.path_downloadfiles.place(x = 140, y = 195)

        exit_button.place(x = 350, y = 250)

        #Call Loop
        self.root.mainloop()

    def salir(self):
        self.month = self.inputtxt.get(1.0, 'end-1c')
        self.password = self.inputpass.get(1.0, 'end-1c')
        self.mailpath = self.inputmail.get(1.0, 'end-1c')
        self.root.destroy()
    
    # Files Folder
    # Set Path
    def setFilesPath(self):
        self.savefilespath = filedialog.askdirectory(initialdir=self.current_dir)
        self.path_savefiles.config(text="Path: " + self.savefilespath)

    def setFilesPath2(self):
        self.downloadfilespath = filedialog.askdirectory(initialdir=self.current_dir)
        self.path_downloadfiles.config(text="Path: " + self.downloadfilespath)

    # Getters
    def getMailpath(self): 
        return self.mailpath
    def getPass(self):
        return self.password
    def getSavePath(self):
        return self.savefilespath
    def getdownloadPath(self):
        return self.downloadfilespath
    def getMonth(self):
        return self.month

# We havo to download multiples files, and with these files we have to rename
# by specific names, so the better way is create a class for each download
class Downloader_scv:
    ''' 
    Initializer
    '''
    def __init__(self, driver:selenium.webdriver, smartgroup:str, soup:str, month:str):
        self.smartgroup = smartgroup  #Type file : BienvenidaProfesionales, BienvenidaEspecialista ...
        self.month = month
        self.driver = driver    #selenium Driver
        self.soup = soup    #Initial Table of the page 'Informes' < 'email'
        self.correct_exported = []# Type : link


    '''
    To get the index in the Informes table by a specific smartgroup
    name and a sppecific month and add it to a list to know the index
    in the main table
    '''
    def filter_informes_index(self) -> list:
        index_val = 1
        index_list = []
        for row in self.soup.find_all('tr'):
            td_values = [value.text for value in row.find_all('td')]
            
            # Verify dont pass to last month
            if td_values[5][5:7] < self.month:
                return index_list

            # Filter by month and smartgroup
            if td_values[5][5:7] == self.month and td_values[2][9:] == self.smartgroup:
                index_list.append(index_val)
            index_val += 1

    '''
    click the elements in the 'INFORMES' < 'email' table by 
    their index positions 
    '''
    def click_Informes_rows(self):
        '''
        With the driver, we navigate to 'INFORMES' < 'email'
        '''
        self.driver.get("https://td45.tripolis.com/dialogue/reports/publishing/emails/executeFilterForReporting.html")

        index_list = self.filter_informes_index()
        for i in index_list:
            self.driver.find_element(By.CSS_SELECTOR,f'tr[id = "table_row{i}"] input[class = "ext_checkbox"]').click()

    '''
    Manage the three types of exports (in order):
        1.  Contacto Entregado ('DELIVERED')
        2.  Apertura ('OPENS')
        3.  Click en cualquier link ('CLICKS_ANY_LINK')
    '''
    def export_type(self):
        # Move to Informes
        self.driver.find_element('id', 'reports').click()

        # Manage 'Delivered'
        self.export_specific('DELIVERED')

        # Manage 'Opnes'
        self.export_specific('OPENS')

        # Manage 'Click_any_link'
        self.export_specific('CLICKS_ANY_LINK')


    '''
    Export a specific type (Apertura, Click en cualquier link o Contacto Entregado)
    Return 1 if the button 'Exportar' is enabled and 0 if it isn't
    '''
    def export_specific(self, specific_type:str) -> int:
        # Move to INFORMES
        self.driver.get('https://td45.tripolis.com/dialogue/reports/publishing/emails/exportJobReport.html')

        # Unselect Send Email
        self.driver.find_element(By.CSS_SELECTOR,'input[id = "sendEmail"]').click()

        # Find the select Box
        select_element = (self.driver.find_element('id',"exportTypeId"))

        # Create a Select object
        select = Select(select_element)

        # Select the option
        select.select_by_value(specific_type) 

        # Find the parent of 'RUT' and 'EMAIL'
        parent = self.driver.find_element(By.CSS_SELECTOR,'ul[class = "ms-optgroup"]')

        # Select 'RUT'
        parent.find_element('id', '50-selectable').click()

        # Select 'EMAIL'
        parent.find_element('id', '53-selectable').click()

        attemps = 0
        while self.click_export(specific_type) == 0:
            # If the button isnt enables, wait 5 second
            # number of attemps = 10
            print(f'Intentando exportar {specific_type}. Intento {attemps}')
            logging.info(f'Intentando exportar {specific_type}. Intento {attemps}')
            time.sleep(5)
            attemps += 1

            if attemps == 10: 
                print(f'No se encontraron datos de {specific_type} para {self.smartgroup}')
                logging.warning(f'No se encontraron datos de {specific_type} para {self.smartgroup}')
                break
        
    '''
    Method to click the export button
    '''
    def click_export(self, e_type):
        # To know if the button is enabled
        if self.driver.find_element('id', 'submitBt').is_enabled():
            self.correct_exported.append((e_type, '/'))
            self.driver.find_element('id', 'submitBt').click()
            return 1
        
        else:
            return 0

    '''
    Get the links of the exported files by a generic link and the specific key
    Append the information to a pair's list (name, link)
    '''
    def get_links(self):
        # Navigate to 'PROCESOS'
        self.driver.get("https://td45.tripolis.com/dialogue/processes/list.html")

        # Get the actual Table
        downloads_soup = BeautifulSoup(self.driver.find_element(By.CSS_SELECTOR,'tbody[class = "tbody"]').get_attribute("outerHTML"), 'html.parser')

        # Get the number of types that exists in the dict (only they have information)
        num = len(self.correct_exported)

        if num == 0:
            return 0

        for i in range(num):
            link = downloads_soup.find('tr', {'id': f'table_row{num-i}'}).find_all('td')[2].find('div').get('onclick')
            
            # Get the file ID
            link = link.split('=')[-1]
            name = self.correct_exported[i][0]

            # Saving the download link
            self.correct_exported[i] = (self.smartgroup+'_'+name, 'https://td45.tripolis.com/dialogue/processes/exportDetail.html?pId='+ link[:-1])
        return 1

    '''
    Download the file by the link in the list and rename the file
    with the smarthgroup name and the type
    '''
    def download_and_rename(self):
        for pair in self.correct_exported:
            print(f'Descargando: {pair[0]}')
            logging.info(f'Descargando: {pair[0]}')
            
            # Download the file page
            self.driver.get(pair[1])

            # Get initial number of files
            initial_files = len(os.listdir(DOWNLOAD_PATH))

            # Select the button 'descargar'
            main_hd = self.driver.find_element('id', 'main-hd')
            main_hd.find_element(By.CSS_SELECTOR, 'li[class = "left"]').click()

            n_times = 1
            while True:
                print(f'Descargando {pair[0]}.... Intento {n_times}')
                logging.info(f'Descargando {pair[0]}.... Intento {n_times}')
                time.sleep(10)

                # Get the new files
                updated_files = len(os.listdir(DOWNLOAD_PATH))

                if (updated_files - initial_files): 
                    print('Archivo descargado')
                    logging.info('Archivo descargado')
                    break
                
                # 10 minutes to download the file
                if n_times > 120:
                    print(f'No se pudo descargar {pair[0]}. Compruebe conexión a internet')
                    logging.warning(f'No se pudo descargar {pair[0]}. Compruebe conexión a internet')
                
                n_times +=1

            #Changing the file name
            # Get a list of all files in the downloads directory
            files = os.listdir(DOWNLOAD_PATH)

            # Filter the list to only include CSV files
            csv_files = [file for file in files if file.endswith('.csv')]

            # Sort the list by modification time (most recent first)
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_PATH, x)), reverse=True)

            if csv_files:
                # Get the most recent CSV file
                last_csv_file = csv_files[0]
            else:
                print("No se ecnontraron archivos descargados")
                logging.warning("No se ecnontraron archivos descargados")

            # Now we have the file name and we can change it 
            os.rename(DOWNLOAD_PATH+'\\'+last_csv_file, SAVE_PATH+'\\'+ pair[0]+'.csv')

    '''
    To manage all methods in the download
    '''
    def manage_downlads(self):
        # Click Rows in Informes < email
        print(f'Clickeando Filas correspondientes a {self.smartgroup}')
        logging.info(f'Clickeando Filas correspondientes a {self.smartgroup}')
        self.click_Informes_rows()
        
        # Export the clicked rows with the three types
        print(f'Exportando archivos de {self.smartgroup}')
        logging.info(f'Exportando archivos de {self.smartgroup}')
        self.export_type()

        # Get the links tho download the files
        exported = self.get_links()

        if not exported:
            print(f'No se encontraron archivos exportados para {self.smartgroup}')
            logging.warning(f'No se encontraron archivos exportados para {self.smartgroup}')
            return

        # Download and rename the files
        print(f'Descargando u renombrando archivos de {self.smartgroup}')
        logging.info(f'Descargando u renombrando archivos de {self.smartgroup}')
        self.download_and_rename()

        return (self.smartgroup, len(self.correct_exported))

'''
Login to Tripolis Page
Receive the driver
'''
def login(driver:selenium.webdriver.firefox.webdriver.WebDriver, domain_, user_, pass_) -> None:

    driver.get("https://td45.tripolis.com/dialogue/login.html")
    #driver.maximize_window() # For maximizing window

    domain = driver.find_element('id',"domainName")
    username = driver.find_element('id',"username")
    password = driver.find_element('id',"password")

    # sending Session's Keys
    domain.send_keys(domain_)
    username.send_keys(user_)
    password.send_keys(pass_)

    # Click in the login button
    driver.find_element('id',"loginButton").click()

    # Current URL to verify the log
    get_url = driver.current_url

    try:
        assert 'https://td45.tripolis.com/dialogue/home.html' == str(get_url)
        return 1

    except AssertionError:
        return 0

"""
To get only values on the month of interest
soup: html of the files
month: month to select
"""
def filter_soup(soup:str, month:str) -> str:
    names_set = set() # To add the smarthgroup
    for row in soup.find_all('tr'):
        td_values = [value.text for value in row.find_all('td')]
        
        # Verify dont pass to last month
        if td_values[5][5:7] < month:
            return names_set

        # get the name
        name = td_values[2]
        # Filter by month and smartgroup and the large (this is to dont get the
        # files with the name 'grupo de prueba')
        if td_values[5][5:7] == month and len(name) > 17:
            name = name[9:]
            names_set.add(name)
    return list(names_set)

def verify_entries(entries, month):
    for i in entries:
        if i == None or i == '':
            print(f'Existe una entrada mal ingresada, intente nuevamente')
            return 1
    if len(month) != 2:
        print('La entrada mes fue mal ingresada')
        return 1

def main():
    # Show windows
    w = WindowTK()
    mail = w.getMailpath()
    save_path = w.getSavePath()
    download_path = w.getdownloadPath()
    client = '__'
    password = w.getPass()
    month_ = w.getMonth()

    # Verifying entries
    if verify_entries([mail, save_path, download_path, password], month_):
        print('Ingrese los datos nuevamente')
        return

    global SAVE_PATH
    global DOWNLOAD_PATH
    global FILE_PATH
    SAVE_PATH = save_path
    DOWNLOAD_PATH = download_path
    FILE_PATH = f'{SAVE_PATH}\info_download_{month_}.log'

    # Log config
    logging.basicConfig(filename=FILE_PATH, encoding='utf-8', level=logging.INFO,
                    format='[%(asctime)s]:[%(levelname)s]:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Print info
    logging.info(f"Programa ejecutado por {mail}")

    driver = webdriver.Firefox()

    # Verify the acces
    if login(driver, client, mail, password): 
        print("Acceso correcto a la pagina de Tripolis")
        logging.info("Acceso correcto a la pagina de Tripolis")
    else:
        print('No se pudo ingresar a la página Verifique las credenciales y vuelva a iniciar')
        driver.quit()
        logging.critical('No se pudo ingresar a la página Verifique las credenciales y vuelva a iniciar')
        close_log()
        return

    # Verify Method
    try:
        parent = driver.find_element(By.CSS_SELECTOR,'select[id = "contact"]')
        parent.find_element(By.XPATH , "//*[text()='Métodos I, II y III - Q4']").click()
    except TimeoutException:
        logging.critical('No se pudo modificar el metodo de Tripolis')
        close_log()
        return

    try:
        # Moving to 'INFORMES' < 'email' and getting the table of the page ('soup')
        driver.get("https://td45.tripolis.com/dialogue/reports/publishing/emails/executeFilterForReporting.html")

        # Select 50 emails - page
        parent = driver.find_element(By.CSS_SELECTOR,'select[name = "maxRows"]')
        parent.find_element(By.CSS_SELECTOR, 'option[value = "50"]').click()
    
    except TimeoutException:
        logging.critical("No se pudo acceder a la lista de mensajes enviados")
        close_log()
        return

    try:
        soup = BeautifulSoup(driver.find_element(By.CSS_SELECTOR,'tbody[class = "tbody"]').get_attribute("outerHTML"), 'html.parser')
        smarthgroups = filter_soup(soup, month_)    
    except Exception as e:
        logging.critical(f"El siguiente error ocurrió al leer smarthgroups {e}")
        close_log()
        return

    files_info = []
    for i in smarthgroups:
        # Creamos un objeto con el smarthgoup
        print(f'----Manejando las descargas de {i}---')
        downloader = Downloader_scv(driver, i, soup, month_)
        
        # Manejamos la descarga Completa del smarthgoup
        files_info.append(downloader.manage_downlads())

    # Close
    close_log()
    driver.quit()


if '__main__' == __name__:
    main()