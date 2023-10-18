import os
from functionality.highlights import get_event_list
import time
import datetime

"""async def remind(ctx):
    events = await get_event_list(ctx, "today")"""
    
async def timer(ctx):
    while True:
        current_datetime = datetime.datetime.now()

        events = await get_event_list(ctx, "today")
        for event in events:
            event_time = event['startDateTime']
            event_time = datetime.datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')
            time_difference = (event_time - current_datetime).seconds/60
            if (time_difference // 60) <= 10:
                    channel = ctx.create_dm()
                    await channel.send(f"You have {event['name']} scheduled , from {event['startTime']} to {event['endTime']}")
                
        time.sleep(60)  # Fetch the time every 5 mins
