import datetime
import discord
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


async def get_events(ctx, arg):
    '''
    function oto extract events from google calendar

    Parameters
    ----------
    ctx : Discord context window
    arg : Discord bot user.

    Returns
    -------
    None.

    '''
    print("in events")
    channel = await ctx.author.create_dm()
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "json", "token.json")
	# If the user has already logged in, the details are extractecd from token.js
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(
            token_file, SCOPES)
    else:
        await channel.send("You are not logged into Google. PLease login using the !ConnectGoogle command")
    print("token found")
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                               maxResults=10, singleEvents=True, 
                                               orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return
    events_parsed=[]
    keys_to_keep=['summary','description','start','end','location']
    for i in events:
        events_parsed.append({key: value for key, value in i.items() if key in keys_to_keep})
    
    for e in events:
        embed = discord.Embed(colour=discord.Colour.magenta(), timestamp=ctx.message.created_at,
                              title="Your Schedule:")
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        embed.add_field(name="Event Name:", value=e['summary'], inline=False)
        embed.add_field(name="Start Time:", value=e['start'], inline=True)
        embed.add_field(name="End Time:", value=e['end'], inline=True)
        if 'location' in e.keys():
            embed.add_field(name="Location:", value=e['location'], inline=False)
        else:
            embed.add_field(name="Location:", value='None', inline=False)
        #embed.add_field(name="Description:", value=e['description'], inline=False)
        await ctx.send(embed=embed)
    
    #adding event to calender
    """event = {
  'summary': 'Trying to add something',
  'location': 'USA',
  'description': 'SE project',
  'start': {
    'dateTime': '2023-10-20T09:00:00-07:00',
    'timeZone': 'America/New_York',
     },
   'end': {
    'dateTime': '2023-10-20T17:00:00-07:00',
    'timeZone': 'America/New_York',
     }
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    """