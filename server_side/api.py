from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from threading import Thread
import requests
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


#based on https://developers.google.com/drive/api/v3/quickstart/python code
def make_creds(SCOPES,F):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                F, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

SERVICE = build('drive','v3',credentials=make_creds(['https://www.googleapis.com/auth/drive'],os.path.join('server_side','credentials.json')))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global SERVICE

        path = self.path
        folder_id = '1EH5AmEtk9RNVxgj7B-pLoKzz_3PkzNDP'
        results = SERVICE.files().list(q="mimeType='video/mp4' and trashed = false",fields="nextPageToken, files(id, name, parents)",pageSize=400).execute()
        videos = []
        for f in results['files']:
            try:
                if folder_id in f['parents']:
                    videos.append(f)
            except KeyError:
                pass
        links = []
        for vid in videos:
            SERVICE.permissions().create(body={"role":"reader", "type":"anyone"}, fileId=vid['id']).execute()
            links.append('https://drive.google.com/uc?export=download&id='+vid['id'])
        
        r = {'links':links}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(r),'utf-8'))
    


server = HTTPServer(('localhost',8000),Handler)
s_t = Thread(target=server.serve_forever,name='server-proc')
s_t.start()

r = requests.get('http://localhost:8000/test/test')
print(r.status_code)
print(r.json())
while True:
    pass