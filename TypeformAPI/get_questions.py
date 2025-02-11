"""
Code to get by the api the questions
"""
import os
import json
import requests
import pandas as pd

DEBUG = True

def get_token():
    """
    Return the token in the json file
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    token_path = os.path.join(current_path, r'keys\token_typeform.json')
    
    # Read the json file and get the token
    with open(token_path, 'r') as file:
        data = json.load(file)

    return data['token']
    
def make_query(form_id, token):
    """
    Makes the GET query
    """

    url = f"https://api.typeform.com/forms/{form_id}"

    # Setting the headers
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Setting the body
    body = {
        
    }

    # Making the query
    try:
        response = requests.get(url, headers=headers, data=body)

        if response.status_code == 200:
            return response.json()

        else:
            print(f"Error: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_data(id, tienda, tipo, value_id):

    token = get_token()

    # Getting the info
    data = make_query(id, token)


    # get the useful data
    form_name = data['title']

    # Getting the questions
    json_questions = data['fields']

    n = 1
    data = {
        "Pregunta": [],
        "ID": [],
        "Ref": [],
        "Enunciado": [],
    }
    for q in json_questions:
       
        try:
            sub_quest = q["properties"]['fields']

            for sq in sub_quest:
                print(f"Pregunta_{n}")

                data["Pregunta"] += [f"Pregunta_{n}"]
                data["Enunciado"] += [sq["title"].strip()]
                data["ID"] += [sq['id']]
                data["Ref"] += [sq['ref']]
                print()
                n+=1
            
        except:
            print(f"Pregunta_{n}")

            data["Pregunta"] += [f"Pregunta_{n}"]
            data["Enunciado"] += [q["title"].strip()]
            data["ID"] += [q['id']]
            data["Ref"] += [q['ref']]
            print()
            n+=1 
    
    df = pd.DataFrame(data)

    if tienda == "client1":
        df['Tienda_ID_Cadena'] = 2
    else: #client2
        df['Tienda_ID_Cadena'] = 1

    if tipo == 'opcion1':
        df['Tienda_Tipo'] = 1

    elif tipo == 'opcion2':
        df['Tienda_Tipo'] = 2
    else:# opcion3
        df['Tienda_Tipo'] = 3

    df['Activo'] = 1
    df['Fecha_Carga'] = pd.Timestamp.now()

    # empieza de value_id y suma 1 por cada fila
    df["TF_IDEncabezado"] = range(value_id, value_id + len(df))

    df = df[["TF_IDEncabezado", "Tienda_ID_Cadena", "Tienda_Tipo",
              "Pregunta", "ID", "Ref", "Enunciado", 'Activo', 'Fecha_Carga']]


    df.to_csv(f"{form_name}_{tienda}.csv", index=False, sep=";")

    return value_id+len(df)


if __name__ == '__main__':
    questions = [
        ("val1","client2", 'opcion2'), 
        ("val2","client2", 'opcion1'), 
        ("val3","client1", 'opcion3'), 
        ("val4","client1", 'opcion2'), 
        ("val5", "client1", 'opcion1') 
    ]
    val = 210
    for q in questions:
        val = get_data(q[0], q[1], q[2], val)