from functionality.shared_functions import create_event_tree, create_type_tree, add_event_to_file, turn_types_to_string
from types import TracebackType
from Event import Event
from parse.match import parse_period
from functionality.create_event_type import create_event_type
from functionality.distance import get_distance
from datetime import datetime, timedelta
from parse.match import parse_period24

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def check_complete(start, start_date, end, end_date, array):
    """
    Function:
        check_complete
    Description:
        Boolean function to check if both the date objects are created
    Input:
        start_date - start date
        end_date - end date
    Output:
        - True if both the date objects are created else False
    """
    if start and end:
        print("Both date objects created")
        array.append(start_date)
        array.append(end_date)
        return True
    else:
        return False


async def add_event(ctx, client):
    """
    Function:
        add_event
    Description:
        Walks a user through the event creation process
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []
    await channel.send("Let's add an event!\n" + "What is the name of your event?:")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    event_array.append(event_msg)
    await channel.send(
        "Now give me the start & end dates for you event. "
        + "You can use 12-hour formatting or 24-hour formatting\n\n"
        + "Here is the format you should follow (Start is first, end is second):\n"
        + "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm (12-hour formatting)\n"
        + "Or mm/dd/yy hh:mm mm/dd/yy hh:mm (24-hour formatting)"

    )

    event_dates = False
    # A loop that keeps running until a user enters correct start and end dates for their event following the required format
    # Adds start and end dates to the array if both are valid
    while not event_dates:
        date_array = []
        msg_content = ""
        start_complete = False
        end_complete = True
        if ctx.message.author != client.user:
            # Waits for user input
            event_msg = await client.wait_for("message", check=check)
            # Strips message to just the text the user entered
            msg_content = event_msg.content

        #print(" yesa  " + str(msg_content))
        if msg_content.__contains__("am") or msg_content.__contains__("pm") or msg_content.__contains__("AM") or msg_content.__contains__("PM"):
            try:
                parse_result = parse_period(msg_content)
            except Exception as e:
                await channel.send(
                    "Looks like "
                    + str(e)
                    + ". Please re-enter your dates.\n"
                    + "Here is the format you should follow (Start is first, end is second):\n"
                    + "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
                start_complete = False
                continue

            start_complete = True

            #print("Lets see for 12 hr it now " + str(parse_result))

            start_date = parse_result[0]
            end_date = parse_result[1]

            # If both datetime objects were successfully created, they get appended to the list and exits the while loop
            if not (event_dates := check_complete(start_complete, start_date, end_complete, end_date, event_array)):
                # If both objects were unsuccessfully created, the bot notifies the user and the loop starts again
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
                date_array = []
                msg_content = ""

        # 24hr format
        else:
            try:
                parse_result = parse_period24(msg_content)
            except Exception as e:
                await channel.send(
                    "Looks like "
                    + str(e)
                    + ". Please re-enter your dates.\n"
                    + "Here is the format you should follow (Start is first, end is second):\n"
                    + "mm/dd/yy hh:mm mm/dd/yy hh:mm "
                )
                start_complete = False
                continue

            start_complete = True

            #print("Lets see it now " + str(parse_result))
            start_date = parse_result[0]
            end_date = parse_result[1]

            flag=0
            # If both datetime objects were successfully created, they get appended to the list and exits the while loop
            if not (event_dates := check_complete(start_complete, start_date, end_complete, end_date, event_array)):
                # If both objects were unsuccessfully created, the bot notifies the user and the loop starts again
                flag+=1
                if flag>3:
                    await channel.send(
                    "Unable to create event due to incorrect time format"
                )
                    return
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): mm/dd/yy hh:mm mm/dd/yy hh:mm"
                )
                date_array = []
                msg_content = ""

    # A loop to error check when user enters priority value
    event_priority_set = False
    while not event_priority_set:
        await channel.send(
            "How important is this event? Enter a number between 1-5.\n\n" +
            "5 - Highest priority.\n" +
            "4 - High priority.\n" +
            "3 - Medium priority.\n" +
            "2 - Low priority.\n" +
            "1 - Lowest priority.\n"
        )

        event_msg = await client.wait_for("message", check=check)  # Waits for user input
        event_msg = event_msg.content  # Strips message to just the text the user entered

        try:
            if 1 <= int(event_msg) <= 5:
                event_array.append(event_msg)
                event_priority_set = True  # if entered value is in the range, loop exits
            else:
                await channel.send(
                    "Please enter a number between 1-5\n")
        except:
            await channel.send(
                "Please enter a number between 1-5\n")  # Handles when user enters non numeric entries
            continue

    create_type_tree(str(ctx.author.id))
    output = turn_types_to_string(str(ctx.author.id))
    await channel.send(
        "Tell me what type of event this is. Here is a list of event types I currently know:\n" + output
    )
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    await create_event_type(ctx, client, event_msg)  # Running event_type creation subroutine
    event_array.append(event_msg)
    await channel.send(
        "What is the location of the event? (Type None for no location)"
    )
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    event_array.append(event_msg)
    dest=event_msg
    print(dest)
    if event_msg !='None':
        await channel.send(
            "Do you want to block travel time for this event?(Yes/No)"
        )
        event_msg = await client.wait_for("message", check=check)  # Waits for user input
        travel_flag = event_msg.content
        if travel_flag =='Yes':
            await channel.send(
                "Enter exact string out of following modes:[DRIVING, WALKING, BICYCLING, TRANSIT])"
            )
            event_msg = await client.wait_for("message", check=check)  # Waits for user input
            mode = event_msg.content
            
            await channel.send(
                "Enter source address"
            )
            event_msg = await client.wait_for("message", check=check)  # Waits for user input
            src = event_msg.content
            travel_time=get_distance(dest,src,mode)
            end=event_array[1]
            strt=(end-timedelta(seconds=travel_time))
            
            
            current = Event("Travel",strt, end, "1", "", "", "")
            await channel.send("Your Travel event was successfully created!")
            create_event_tree(str(ctx.author.id))
            add_event_to_file(str(ctx.author.id), current)
            
            
            
            
            
        
    await channel.send("Any additional description you want me to add about the event? If not, enter 'done'")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    if event_msg.lower() == "done":
        event_array.append("")
        print(event_array)

        #adding to GCalender
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
        new_event = {
            'summary': event_array[0],
            'location':event_array[-2],
            'description': event_array[-1],
            'start':{
                'dateTime': event_array[1].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone':'America/New_York'
            },
            'end':{
                'dateTime': event_array[2].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone':'America/New_York'
            }
        }
        event = service.events().insert(calendarId='primary', body=new_event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))
    else:
        event_array.append(event_msg)
    



    # Tries to create an Event object from the user input
    try:
        current = Event(event_array[0], event_array[1], event_array[2], event_array[3], event_array[4], event_array[6],event_array[5])
        await channel.send("Your event was successfully created!!")
        await channel.send('Event created: %s' % (event.get('htmlLink')))
        create_event_tree(str(ctx.author.id))
        add_event_to_file(str(ctx.author.id), current)
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)
        TracebackType.print_exc()
        await channel.send(
            "There was an error in creating your event. Make sure your formatting is correct and try creating the event again."
        )
