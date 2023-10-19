from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import sys
import json



async def connect_google(ctx):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds=None
    api_key_1 = None  # apikey for maps distance matrix
    # the api key is stored as a local json. refer to readme for more instructions
    user_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"json", "user_data.json")
    print(user_data)
    channel = await ctx.author.create_dm()
    await channel.send("We will now connect to google calendar")
    key_data = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "json", "key.json")
    if not os.path.exists(key_data):
        print('''Api Key file does not exist. Please refer to readme to add key and restart program''')
        await channel.send('''Api Key file does not exist. Please refer to readme to add key and restart program''')
        sys.exit("Thank You for Using ScheduleBot")
        return 0
    with open(key_data) as json_file:
        data = json.load(json_file)
        api_key_1 = data["key"]
        print("key found")
    #loading the api key from json file. Due to security reasons, we store the key locally
        #our private machines as a json file which is ignored by github which making changes
    # This function checks if the login details of the user are available with us
    cred_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "json", "credentials.json")
    token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "json", "token.json")
    # If the user has already logged in, the details are extractecd from token.js
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(
            token_file, SCOPES)
    # if the user has not logged in/ his credentials have expired, 
    #the user is prompted to login and the details are stored in token.json
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            await channel.send("Please check the tab in your browser for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
            await channel.send("Login Successful")
            print("Login Successfull")
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    await channel.send("You are now connected to Google.")
    return 1