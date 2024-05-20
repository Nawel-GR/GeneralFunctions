from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def auth():
  creds = None
  if Path(r"keys\token.json").exists():
      creds = Credentials.from_authorized_user_file(r"keys\token.json", SCOPES)
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(r"keys\credentials.json", SCOPES)
          creds = flow.run_local_server(port=0)
      with open(r"keys\token.json", "w") as token:
          token.write(creds.to_json())

  return creds

import base64
from email.message import EmailMessage

def send_email(subject, body, to_email, from_email):
  creds = auth()
  
  with build("gmail", "v1", credentials=creds) as service:
      message = EmailMessage()
      message.set_content(body)

      message["To"] = to_email
      message["From"] = from_email
      message["Subject"] = subject

      encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

      create_message = {"raw": encoded_message}
      send_message = service.users().messages().send(userId="me", body=create_message).execute()
      print(f"Message Id: {send_message['id']}")
