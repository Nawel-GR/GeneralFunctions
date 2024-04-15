import pyodbc
import pandas as pd

""" CONNECTIONS TO SQL SERVER 2014
    This module contains the functions to connect to a SQL Server 2014
"""

def bbdd_to_sql(df, Server, Database, User, Password, table, Driver = 'SQL Server'):
    '''Uploads the dataframe on the SQL BBDD by the iteraccion over the rows
    Args:
        df: pd.DataFrame -> The pandas dataframe that has the Vtex Information
        Server: str -> The Servers that contains the Database
        Database: str -> The database that contains the table
        User:str -> The user's name
        Password:str -> The user's password
        table: str -> The table to upload the information
        Driver: str -> The driver to make the connection with the database
    '''
    # Making the connection
    conn = pyodbc.connect(f'Driver={Driver};Server={Server};Database={Database};UID={User};PWD={Password}')

    cursor = conn.cursor()

    # Upload the new info
    columns = '], ['.join(df.columns)

    query = f"INSERT {table} ([{columns}]) "

    for index, row in df.iterrows():
        # column join
        values = "', '".join([str(i) for i in row])
        to_query = f"VALUES ('{values}')"
        n_query = query + to_query
        cursor.execute(n_query)

    conn.commit()
    conn.close()


def get_from_sql(Server, Database, User, Password, table, Driver = 'SQL Server'):
    '''Downloads the information from the SQL BBDD
    Args:
        Server : The Servers that contains the Database
        Database : The database that contains the table
        User : The user's name
        Password : The user's password
        table : the table to upload the information
        Driver : the driver to make the connection with the database
    Returns:
        rows : the information of the table
    '''
    # Making the connection
    conn = pyodbc.connect(f'Driver={Driver};Server={Server};Database={Database};UID={User};PWD={Password}')
    
    # Getting the information
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

