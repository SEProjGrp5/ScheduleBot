import re
import datetime
from functionality.shared_functions import read_event_file, create_event_tree


async def get_highlight(ctx, arg):
    """
    Function:
        get_highlight
    Description:
        Shows the events planned for the day by the user.
    Input:
        - ctx - Discord context window
        - arg - The input arguments which specify the date
    Output:
        - A message sent to the context with all the events that start and/or end today
    """
    # Get the date
    day = get_date(arg)

    # Open and read user's calendar file
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id))

    print(str(ctx.author.id))
    print("\n\n\n\n\n")

    
    # Initialize variables
    channel = await ctx.author.create_dm()
    event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': '','loc': ''}
    events = []

    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
            print(row)
            event['name'] = row[1]
            start = row[2].split()
            event['startDate'] = start[0]
            event['startTime'] = convert_to_12(start[1][:-3])  # Convert to 12 hour format
            end = row[3].split()
            event['endDate'] = end[0]
            event['endTime'] = convert_to_12(end[1][:-3])  # Convert to 12 hour format
            event['type'] = row[4]
            event['desc'] = row[5]
            event['location']=row[6]
            dates = [event['startDate'], event['endDate']]

            flag = check_start_or_end(dates, day)

            if flag == 1:
                # If event starts and ends today
                event['flag'] = 1
                events.append(event)
            elif flag == 2:
                # If event starts today but ends on a later date
                event['endDate'] = event['endDate'].split('-')
                event['endDate'] = event['endDate'][1] + '/' + event['endDate'][2] + '/' + event['endDate'][0]
                event['flag'] = 2
                events.append(event)
            elif flag == 3:
                # If event is already in process and ends today
                event['flag'] = 3
                events.append(event)

            # reset event
            event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}

        # If events are on schedule for today
        if len(events) != 0:
            for e in events:
                if e['flag'] == 1:
                    await channel.send(f"You have {e['name']} scheduled , from {e['startTime']} to {e['endTime']}")
                elif e['flag'] == 2:
                    await channel.send(
                        "You have {e['name']} scheduled, from {e['startTime']} to {e['endTime']} on {e['endDate']}")
                elif e['flag'] == 3:
                    await channel.send(f"You have {e['name']} scheduled, till {e['endTime']}")
        else:
            if day is None:
                await channel.send("Incorrect input format. \nHere is the format you should follow:\n!day "
                                   "today\\tomorrow\\yesterday\n!day 3 (3 days from now)\n!day -3 (3 days ago)\n!day "
                                   "4/20/22 (On Apr 20, 2022)")
            else:
                await channel.send("You don't have any event scheduled for " + day + "!")
    else:
        await channel.send("Looks like your schedule is empty. You can add events using the '!schedule' command!")


# Helper Functions

def get_date(arg):
    """
    Function:
        get_date
    Description:
        Get the date from the argument
    Input:
        - arg - User input argument
    Output:
        - The date extract from the argument
    """
    if re.match("tomorrow", arg, re.I):
        return str(datetime.date.today() + datetime.timedelta(days=1)).split()[0]
    if re.match("yesterday", arg, re.I):
        return str(datetime.date.today() - datetime.timedelta(days=1)).split()[0]
    if re.fullmatch("\d", arg) is not None:
        return str(datetime.date.today() + datetime.timedelta(days=int(arg))).split()[0]
    if re.fullmatch("-\d", arg) is not None:
        arg = arg.replace("-", "")
        return str(datetime.date.today() - datetime.timedelta(days=int(arg))).split()[0]
    if re.fullmatch("\d\d/\d\d/\d\d", arg):
        return str(datetime.datetime.strptime(arg, "%m/%d/%y")).split()[0]
    if re.match("today", arg, re.I):
        return str(datetime.date.today()).split()[0]
    else:
        return None



def check_start_or_end(dates, today):
    """
    Function:
        check_start_or_end
    Description:
        checks if given date starts or ends today
    Input:
        - dates - a list containing start and end date (strings) for an event
        - today - today's date (string)
    Output:
        - 0 if no event starts or ends today
        - 1 if event starts and ends today
        - 2 if event starts today and ends on a later date
        - 3 if event started on a previous date and ends today
    """
    if today == dates[0]:
        if today == dates[1]:
            return 1
        else:
            return 2
    elif today == dates[1]:
        return 3
    else:
        return 0


def convert_to_12(time):
    """
    Function:
        conver_to_12
    Description:
        Converts 24 hour time to 12 hour format
    Input:
        - time - time string in 24 hour format
    Output:
        - time string converted to 12 hour format
    """
    if int(time[:2]) > 12:
        new_time = str(int(time[:2]) - 12) + ":" + time[3:] + " PM"
    elif int(time[:2]) == 0:
        new_time = "12:" + time[3:] + " AM"
    elif int(time[:2]) == 12:
        new_time = time + " PM"
    elif int(time[:2]) > 9 and int(time[:2]) < 12:
        new_time = time + " AM"
    else:
        new_time = time[1:] + " AM"
    return new_time

# test()

async def get_event_list(ctx, arg):
    """
    Function:
        get_highlight
    Description:
        Shows the events planned for the day by the user.
    Input:
        - ctx - Discord context window
        - arg - The input arguments which specify the date
    Output:
        - A message sent to the context with all the events that start and/or end today
    """
    # Get the date
    day = get_date(arg)

    # Open and read user's calendar file
    create_event_tree(str(ctx.id))
    rows = read_event_file(str(ctx.id))
    
    # Initialize variables
    event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': '','loc': ''}
    events = []

    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
            #print(row)
            event['name'] = row[1]
            event['startDateTime'] = row[2]
            event['endDateTime'] = row[3]
            event['type'] = row[4]
            event['desc'] = row[5]
            event['location'] = row[6]
            events.append(event)

    return events
           