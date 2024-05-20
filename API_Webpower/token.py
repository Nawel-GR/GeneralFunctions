import requests

"""To use
token_obj = Token(client_id, client_secret, token_url)
    
# Getting access token
token_obj.create_token()

token = token_obj.get_token()
"""

class Token():
    def __init__(self, client_id:str, client_secret:str, token_url:str):
        """ Create a token by init values.
        Args :
            client_id (str) : Clietn ID
            client_secret (str) : Client Credentials Key
            token_url (str) : Endpoint token
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

        self._access_token = None
        self._expire_time = None

        # Creating Token
        if not self.create_token():
            raise ValueError("Can't create a token, check the credentials.")


    def create_token(self) -> int:
        """
        Method that tries create a new token 
        with the init params of the opbject.

        Args :

        Return : 
            response (int) : 1 if set a new token, 0 if not
        """

        # verification data
        verification_data = {
        'grant_type' : 'client_credentials',
        'client_id' : self.client_id,
        'client_secret' : self.client_secret,
        'scope': 'rest'
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.token_url, data = verification_data, headers = headers)
        token_response = response.json()

        # Verifying the response
        if 'access_token' in token_response:
            self._access_token = token_response['access_token']
            self._expire_time = token_response['expires_in']
            return 1

        else:
            print('Authentication error:', token_response['error_description'])
            return 0
        
    def get_token(self,) -> str:
        """
        Returns the actual access token to APIs comunnication
        
        Args : 

        Rerturn :
            Access_token (str) : Actual Access token 

        """
        return self._access_token
    
    def get_expiration_time(self,) -> str:
        """
        Returns the expiration's time for the actual token
        
        Args : 

        Rerturn :
            Expiration time (str) : Actual expiration time

        """
        return self._expire_time
