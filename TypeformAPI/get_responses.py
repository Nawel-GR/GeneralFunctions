"""

"""
import requests
import os
import json
from get_questions import get_token
from utils import convert_chilean_datetime
import pandas as pd

DEBUG = False

def make_query(form_id, token, since, until, page_size, before = None, response_type = "completed"):
    """ Makes the GET query
    Args:
        form_id (str): The form id
        token (str): The token
        since (str): The date since
        until (str): The date until
        page_size (int): The page size
        before (str): The date before
    Rteturns:
        dict: The json response
    """

    url = f"https://api.typeform.com/forms/{form_id}/responses"

    # Setting the headers
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Setting the body
    params = {
        "page_size" : page_size,
        "since" : since,
        "until" : until,
        "response_type" : response_type
    }

    # Addng the before parameter if it exists
    if before is not None:
        params["before"] = before

    # Making the query
    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()

        else:
            print(f"Error: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_all_responses(json_data, version = '1'):
    """
    """
    number = 1
    answers = {}

    try:
        answers["boleta"] = json_data["hidden"]["n_boleta"]
    except KeyError:
        answers["boleta"] = None
    try:
        answers["email"] = json_data["hidden"]["correo_electronico"]
    except KeyError:
        answers["email"] = None

    answers["version"] = version
    answers["response_type"] = json_data["response_type"]
    answers["landed_at"] = convert_chilean_datetime(json_data["landed_at"])

    for answer in json_data["answers"]:
        number += 1
        
        if answer['type'] == "number":
            answers[answer['field']['ref']] = answer['number']
            #print(f"Answer: {answer['number']}")
        
        elif answer['type'] == "boolean":
            answers[answer['field']['ref']]  = answer['boolean']
            #print(f"Answer: {answer['boolean']}")
        
        elif answer["type"] == "choice":
            answers[answer['field']['ref']]  = answer['choice']['label']
            #print(f"Answer: {answer['choice']['label']}")

        elif answer["type"] == "choices":
            # Concatenate all the labels
            l = []     
            for label in answer['choices']['labels']:
                l.append(label)

            stri = ";".join(l)
            answers[answer['field']['ref']]  = stri
    
    #Print dict
    if DEBUG:
        for key, value in answers.items():
            print(f"{key}: {value}")

    return answers


def get_data_responses(id):
    
    token = get_token()

    # Getting the info
    since = "2023-12-10T00:00:00" #mod
    until = "2024-12-12T00:00:00" #mod
    page_size = 500
    before = None

    data = make_query(id, token, since, until, page_size, before)

    # Get items
    items = data["items"]

    counter = 1
    page_count = data['page_count']

    responses = []

    if DEBUG: print(f"Pages: {page_count}")

    for i in items:
        if DEBUG:
            print(f"Response {counter}")
            print(f"token : {i['token']}")
            print()
        responses.append(get_all_responses(i))
        counter += 1

    while page_count > 1:

        # Getting the token
        before = items[-1]['token']

        data = make_query(id, token, since, until, page_size, before)

        # Get items
        items = data["items"]

        page_count = data['page_count']

        print(f"Pages: {page_count}")

        for i in items:
            if DEBUG:
                print(f"Response {counter}")
                print(f"token : {i['token']}")
                print()
            responses.append(get_all_responses(i))
            counter += 1

    print(f"Total responses: {len(responses)}")
    
    return responses

def main(id, name):
    data_responses = get_data_responses(id)

    data_questions = pd.read_csv(f"{name}.csv")

    columns_values = []
    columns_values.append("boleta")
    columns_values.append("email")
    columns_values.append("version")
    columns_values.append("response_type")
    columns_values.append("landed_at")

    # Create a DataFrame with the questions 
    values_ref = list(data_questions['Ref'].unique())

    columns_values += values_ref

    bbdd_responses = pd.DataFrame(columns=columns_values)

    bbdd_responses = pd.concat([bbdd_responses, pd.DataFrame(data_responses)], ignore_index=True)

    for index, row in data_questions.iterrows():
        bbdd_responses.rename(columns={row['Ref']: row['Pregunta']}, inplace=True)

    bbdd_responses.to_csv(f"bbdd_{name}_V2.csv", index=False)

if __name__ == "__main__":
    # Getting the token
    questions = [
        ("val1","TIENDAS  - op1"), 
        ("val2","TIENDAS  - op2"),
        ("val3","TIENDAS  - op3"), 
        ("val4","TIENDAS  - op1"), 
        ("val5", "TIENDAS  - op2") 
    ]
    
    for q in questions:
        main(q[0], q[1])
