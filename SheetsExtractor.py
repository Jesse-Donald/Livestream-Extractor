import json
import google
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from getConfig import getConfig

def getTimes():

    request = google.auth.transport.requests.Request()

    config = getConfig()

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(request)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


        # Build the service to access the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

        # Write the values to the Google Sheet
    result = (
            sheet.values()
            .get(spreadsheetId=config['SpreadsheetID'], range=config['SpreadsheetName'] + '!A1:D2')
            .execute()
        )
    values = result.get("values", [])

    i = 0
    jsondict = {}
    while i < 4:
       jsondict[values[0][i]] = values[1][i]
        i+=1
    
    with open('times.json', 'w') as token:
            token.write(json.dumps(jsondict))
