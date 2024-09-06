#!/usr/bin/env python3

import sys
import time
import requests
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)
import threading
sys.path.append('../')
from obswebsocket import obsws, events  # noqa: E402
import websocket
import json
import google
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


from getConfig import getconfig

config = getConfig()


request = google.auth.transport.requests.Request()
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

current_item = ''
started_flag = 0
ended_flag = 0
streaming = False
running = True
stream_start = ''
stream_end = ''
sermon_start = ''
sermon_end = ''
# Define the WebSocket URL of your OpenLP instance
ws_url = config['OpenLPIPAddress'] + ":4317"

# Define the message to authenticate with OpenLP
auth_message = {
    "method": "authenticate",
    "params": {
        "username": config["OpenLPUsername"],
        "password": config['OpenLPpassword']  # Replace with your OpenLP password
    },
    "jsonrpc": "2.0",
    "id": 1
}

# Define the message to subscribe to events
subscribe_message = {
    "method": "subscribe",
    "params": {
        "type": "controller"
    },
    "jsonrpc": "2.0",
    "id": 2
}

# Define the credentials file path
credentials_path = 'path/to/your/credentials.json'

# Define the ID of the Google Sheet
spreadsheet_id = config['SpreadsheetID']

def on_message(ws, message):
    data = json.loads(message)
    r = requests.get('http://' + config['OpenLPIPAddress'] + ':4316/api/v2/controller/live-items')
    #print("Received message:")
    #print(json.dumps(data, indent=4))
    print(json.loads(r.content)['title'])
    global current_item
    current_item = json.loads(r.content)['title']
    time.sleep(1)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection established")
    # Authenticate with OpenLP
    ws.send(json.dumps(auth_message))
    # Subscribe to events
    ws.send(json.dumps(subscribe_message))

def run_openlp():
    #websocket.enableTrace(True)
    # Connect to the WebSocket server
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
#    ws.on_open = on_open
    # Run the WebSocket client

    ws.run_forever()

host = config['OBSIPAddress']
port = 4455
password = config['OBSpassword']

def on_connect(obs):
    print("on_connect({})".format(obs))


def on_disconnect(obs):
    print("on_disconnect({})".format(obs))

def on_stream(message):
    global streaming
    global stream_end
    global stream_start
    if "ING" not in str(message):
        if "True"in str(message):
            print("Stream Started!")
            streaming = True
            stream_start = datetime.now()
        else:
            print('Stream Ended!')
            streaming = False
            stream_end  = datetime.now()


obs = obsws(host, port, password, authreconnect=1, on_connect=on_connect, on_disconnect=on_disconnect)
#ws.register(on_event)
obs.register(on_stream, events.RecordStateChanged)
obs.connect()

try:
    openlp = threading.Thread(target=run_openlp)
    openlp.start()
    while running:
        if streaming:
            if current_item == 'Preaching' and started_flag == 0:
                print("Started")
                started_flag = 1
                sermon_start = datetime.now()
            elif current_item != '0010.png' and started_flag == 1 and ended_flag == 0:
               print("Ended!")
               ended_flag = 1
               sermon_end = datetime.now()
        elif started_flag == 1:
            print("Stream Start: " + str(stream_start.isoformat()))
            print("Sermon Start: " + str(sermon_start.isoformat()))
            print("Sermon End: " + str(sermon_end.isoformat()))
            print("Stream End: " + str(stream_end.isoformat()))
            running = False

except KeyboardInterrupt:
    pass

obs.disconnect()

    # Build the service to access the Google Sheets API
service = build('sheets', 'v4', credentials=creds)

    # Write the values to the Google Sheet
values = [[stream_start.isoformat(), sermon_start.isoformat(), sermon_end.isoformat(), stream_end.isoformat()]]
body = {'values': values}
result = service.spreadsheets().values().append(
spreadsheetId=spreadsheet_id, range='Stream/Sermon Times!A2', valueInputOption='RAW', body=body).execute()

print('Variables successfully written to Google Sheet.')
