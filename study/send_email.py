import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    env_folder = os.getenv('ENV_FOLDER')
    creds_path = os.path.join(env_folder, 'token.json')
    credentials_path = os.path.join(env_folder, 'credentials.json')

    if os.path.exists(creds_path):
        creds = Credentials.from_authorized_user_file(creds_path, SCOPES)
        print("Found token.json, loading credentials...")
    else:
        print("token.json not found, initiating OAuth flow...")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Credentials expired, refreshing...")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            print("OAuth flow completed, credentials obtained.")
        with open(creds_path, 'w') as token:
            token.write(creds.to_json())
            print("Credentials saved to token.json.")

    service = build('gmail', 'v1', credentials=creds)
    print("Gmail service built successfully.")
    return service

def send_email(user_email, subject, html_content):
    service = get_gmail_service()
    
    message = MIMEMultipart()
    message['to'] = user_email
    message['subject'] = subject
    message.attach(MIMEText(html_content, 'html'))
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}
    
    try:
        message = service.users().messages().send(userId='me', body=message_body).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None