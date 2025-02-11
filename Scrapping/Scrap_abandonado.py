'''
Code to Download "Carro Abandonado"
Author: Nahuel Gómez Raguileo
'''
import os
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time

import Tripolis as Trip

import CREDENTIALS as C

# Setting paremeters:


# Path to save the files
global SAVE_PATH

# user's keys
###########################################################################
# Download Paths: Path of the downloaded files
download_path = C.DOWNLOAD_PATH

# Client
domain_ = C.DOMAIN

# User
user_ = C.USER

# Password
pass_ = C.PASS
###########################################################################



class Downloader_Abandonado:
    
    def __init__(self, driver:selenium.webdriver, name:str, pos:int, first = False):

        self.driver = driver # Web page driver
        self.name = name # Name of the wave (1, 2 or 3)
        self.pos = pos # Postion of the node in the 'soup' to select it
        self.correct_exported = []# downloadname: bool

        if  not first:
            self.move()

        self.manage_downloads()

    """
    Move to the nodes's page
    """
    def move(self):
        # Moving to 'Informes' < 'Campaign flows'
        self.driver.get("https://td45.tripolis.com/dialogue/reports/publishing/campaigns.html")

        # Selecting campaign
        self.driver.find_element(By.CSS_SELECTOR, 'a[href = "#ac1"]').click()

        # Click span
        self.driver.find_element(By.CSS_SELECTOR, 'span[class = "dynatree-expander"]').click()

        # Click carro abandonado Enero
        self.driver.find_element(By.CSS_SELECTOR, 'span[class = "dynatree-node dynatree-exp-c dynatree-ico-c"]').click()

        # Wait Tripolis response
        wait_nodes_response(self.driver)

        # Move to list of nodes
        self.driver.find_element(By.XPATH, "//a[contains(text(),'nodes')]").click()


    """
    Select the node and export it 
    """
    def select_and_export_options(self):
        print(f"Exportande información de {self.name}")

        # Select the wave
        self.driver.find_element(By.CSS_SELECTOR,f'tr[id = "table_row{self.pos}"] input[class = "ext_checkbox"]').click()

        # Export the wave
        # Se necesita esperar
        self.driver.find_element('id', 'reports').click()

        # Manage 'Delivered'
        self.export_type('DELIVERED')

        # Manage 'Opnes'
        self.export_type('OPENS')

        # Manage 'Click_any_link'
        self.export_type('CLICKS_ANY_LINK')

    '''
    export the specific e_type
    '''
    def export_type(self, e_type:str):

        self.driver.get('https://td45.tripolis.com/dialogue/reports/publishing/campaigns/exportJobReport.html')

        # Unselect Send Email
        self.driver.find_element(By.CSS_SELECTOR,'input[id = "sendEmail"]').click()

        # Find the select Box
        select_element = (self.driver.find_element('id',"exportTypeId"))

        # Create a Select object
        select = Select(select_element)

        select.select_by_value(e_type)

        # Find the parent of 'FECHA_ABANDONO', 'EMAIL' and 'RUT_CLIENTE'
        parent = self.driver.find_element(By.CSS_SELECTOR,'ul[class = "ms-optgroup"]')

        # Select 'FECHA_ABANDONO'
        parent.find_element('id', '50-selectable').click()

        # Select 'EMAIL_CLIENTE'
        parent.find_element('id', '52-selectable').click()

        # Selcet 'RUT_CLIENTE'
        parent.find_element('id', '53-selectable').click()

        attemps = 0
        while self.click_export(e_type) == 0:
            # If the button isnt enables, wait 5 second
            # number of attemps = 10
            print(f'Intentando exportar {e_type}. Intento {attemps}')
            time.sleep(5)
            attemps += 1

            if attemps == 10: 
                print(f'No se encontraron datos de {e_type} para {self.name}')
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
            
            # Get the actual status of the query
            status = downloads_soup.find('tr', {'id':f'table_row{1}'}).find_all('td')[3].find('img').get('src')

            # verify status
            if status != '/dialogue/images/home/alert-g.gif':
                wait_return, downloads_soup = self.waitStatus(status)
                if not wait_return:
                    print(f'La query número {i} de los datos de {self.name} no fue realizada con exito, cancelando descarga...')
                    print('Continuando con las demás descargas')
                    continue

            # Get the file ID
            link = link.split('=')[-1]
            type_id = self.correct_exported[i][0]

            # Saving the download link
            self.correct_exported[i] = (self.name+'_'+str(type_id), 'https://td45.tripolis.com/dialogue/processes/exportDetail.html?pId='+ link[:-1])
        return 1
    
    def waitStatus(self, status):
        if status == '/dialogue/images/home/alert-y.gif':
            
            while status != '/dialogue/images/home/alert-g.gif':
                # we need to wait to the status -g
                time.sleep(10)

                # Refresh the page
                self.driver.refresh()   
                
                # Get the actual Page
                downloads_soup = BeautifulSoup(self.driver.find_element(By.CSS_SELECTOR,'tbody[class = "tbody"]').get_attribute("outerHTML"), 'html.parser')
                status = downloads_soup.find('tr', {'id':f'table_row{1}'}).find_all('td')[3].find('img').get('src')
            

            return (1, downloads_soup)
        else:
            return (0,0)



    '''
    Download the file by the link in the list and rename the file
    with the smarthgroup name and the type
    '''
    def download_and_rename(self):
        for pair in self.correct_exported:
            print(f'Descargando: {pair[0]}')
            
            # Download the file page
            self.driver.get(pair[1])

            # Get initial number of files
            initial_files = len(os.listdir(download_path))

            # Select the button 'descargar'
            main_hd = self.driver.find_element('id', 'main-hd')
            main_hd.find_element(By.CSS_SELECTOR, 'li[class = "left"]').click()

            n_times = 1
            while True:
                print(f'Descargando {pair[0]}.... Intento {n_times}')
                time.sleep(10)

                # Get the new files
                updated_files = len(os.listdir(download_path))

                if (updated_files - initial_files): 
                    print('Archivo descargado')
                    break
                
                # 10 minutes to download the file
                if n_times > 120:
                    print(f'No se pudo descargar {pair[0]}. Compruebe conexión a internet')
                
                n_times +=1

            #Changing the file name
            # Get a list of all files in the downloads directory
            files = os.listdir(download_path)

            # Filter the list to only include CSV files
            csv_files = [file for file in files if file.endswith('.csv')]

            # Sort the list by modification time (most recent first)
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)

            if csv_files:
                # Get the most recent CSV file
                last_csv_file = csv_files[0]
            else:
                print("No se encontraron archivos .csv en el directorio especificado.")

            # Now we have the file name and we can change it 
            os.rename(download_path+'\\'+last_csv_file, SAVE_PATH+'\\'+ pair[0]+'.csv')

    """
    main function that manage the downloads
    """
    def manage_downloads(self):
        self.select_and_export_options()
        
        # Get the links tho download the files
        exported = self.get_links()

        if not exported:
            print(f'No se encontraron archivos exportados para {self.smartgroup}')
            return
        
        # Download and rename the files
        print(f'Descargando y renombrando archivos de {self.name}')
        self.download_and_rename()




"""
Get the nodes in the soup-page and return a list ordered in descending
order with the index position and the number of sends
in: Soup of the node's table
out: list of the nodes ordered in descending 
"""
def order_nodes(soup:str) -> list:
    order = {}
    index = 1
    for row in soup.find_all('tr'):
        td_values = [value.text for value in row.find_all('td')]
        # value 
        val = int(td_values[6].strip().split('/')[0].strip())
        order[index] = val

        index += 1

    # Order the dict and transform it to a list
    sorted_list = sorted(order.items(), key=lambda x: x[1], reverse=True)

    return sorted_list

def wait_nodes_response(driver):
    count = 0
    while driver.current_url == 'https://td45.tripolis.com/dialogue/reports/publishing/campaigns.html':
        if count > 30:
            print('La página Carro Abandonado de Tripolis no responde')
            driver.quit()
            return 0
        time.sleep(10)
        count +=1
    
    return 1


def main(save_path:str, driver):

    global SAVE_PATH
    SAVE_PATH = save_path

    # Verify the acces
    if Trip.login(driver): 
        print("Correct access")
    else:
        print('No se pudo ingresar a la página Verifique las credenciales y vuelva a iniciar')
        driver.quit()

    # Verify Method
    parent = driver.find_element(By.CSS_SELECTOR,'select[id = "contact"]')
    parent.find_element(By.XPATH , "//*[text()='Método IV - Carro Abandonado']").click()

    # Moving to 'Informes' < 'Campaign flows'
    driver.get("https://td45.tripolis.com/dialogue/reports/publishing/campaigns.html")

    # Selecting campaign
    driver.find_element(By.CSS_SELECTOR, 'a[href = "#ac1"]').click()
    
    # Find Text
    parent = driver.find_element(By.XPATH , "//*[text()='CarroAbandonado2022_TRP_CT_PRODUCTOS_V2']")
    
    # Find Father
    parent = parent.find_element(By.XPATH , "./parent::span")
    
    #Click Span
    parent.find_element(By.CSS_SELECTOR, 'span[class = "dynatree-expander"]').click()
    
    # Click Method
    driver.find_element(By.CSS_SELECTOR, 'span[class = "dynatree-node dynatree-exp-c dynatree-ico-c"]').click()

    # waiting for the response
    if not wait_nodes_response(driver):
        return

    # Move to list of nodes
    driver.find_element(By.XPATH, "//a[contains(text(),'nodes')]").click()

    # Create a soup
    soup = BeautifulSoup(driver.find_element(By.CSS_SELECTOR,'tbody[class = "tbody"]').get_attribute("outerHTML"), 'html.parser')
    
    # Sorted List
    s_list = order_nodes(soup)

    # Waves
    print(f'----Manejando las descargas de wave 1---')
    Downloader_Abandonado(driver, 'wave_1', s_list[0][0], True)

    for i in range(2,4):
        print(f'----Manejando las descargas de wave {i}---')
        input()
        Downloader_Abandonado(driver, f'wave_{i}', s_list[i-1][0])


    return



from selenium import webdriver

if '__main__' == __name__:
    driver = webdriver.Firefox()
    path = r""
    main(path,driver )