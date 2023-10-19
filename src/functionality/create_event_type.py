import re
import os
import csv
from datetime import datetime
from types import TracebackType
from event_type import event_type
from functionality.shared_functions import create_type_directory, create_type_file
from functionality.shared_functions import load_key, decrypt_file, encrypt_file


async def create_event_type(ctx, client, event_msg):
    """
    Function:
        create_event_type
    Description:
        Walks a user through the creation of types of event or updating time range for existing event types
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event type added to the user's calendar file or the time range will be update for the existing event type
        - A message sent to the context saying an event type was successfully added or updated
    """

    channel = await ctx.author.create_dm()
    print(ctx.author.id)

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []
    # await channel.send("First give me the type of your event:")
    # event_msg = await client.wait_for("message", check=check)  # Waits for user input
    # event_msg = event_msg.content  # Strips message to just the text the user entered
    event_array.append(event_msg)
    await channel.send(
        "Now give me your perefered time range this event type.\n"
        + "Make sure you include 'am' or 'pm' so I know what is the range of your event, \n"
        + "Here is the format you should follow (Start is first, end is second):\n"
        + "hh:mm am/pm hh:mm am/pm"
    )

    time_range = False
    # A loop that keeps running until a user enters correct start and end time for their event type following the required format
    # Adds start and end time to the array if both are valid
    while not time_range:
        time_array = []
        msg_content = ""
        start_complete = False
        end_complete = True
        if ctx.message.author != client.user:
            # Waits for user input
            event_msg = await client.wait_for("message", check=check)
            # Strips message to just the text the user entered
            msg_content = event_msg.content
            # Splits response to prepare data to be appended to event_array
            time_array = re.split("\s", msg_content)

        try:
            start_time = datetime.strptime(
                time_array[0] + " " + time_array[1], "%I:%M %p"
            )
            start_complete = True
            print("Created start_time object: " + str(start_time))
        except Exception as e:
            print(e)
            await channel.send(
                "Looks like you didn't enter your start time correctly. Please re-enter your time.\n"
                + "Here is the format you should follow (Start is first, end is second):\n"
                + "hh:mm am/pm hh:mm am/pm"
            )
            start_complete = False
            continue

        # Tries to create the end_time datetime object
        try:
            end_time = datetime.strptime(time_array[2] + " " + time_array[3], "%I:%M %p")
            end_complete = True
            print("Created end_time object: " + str(end_time))
        except Exception as e:
            print(e)
            await channel.send(
                "Looks like you didn't enter your end time correctly. Please re-enter your time.\n"
                + "Here is the format you should follow (Start is first, end is second):\n"
                + "hh:mm am/pm hh:mm am/pm"
            )
            end_complete = False
            continue

        # Tries to create the end_time datetime object
        if end_time <= start_time:
            await channel.send(
                "Looks like your end time is before your start time. Please re-enter your time.\n"
                + "Here is the format you should follow (Start is first, end is second):\n"
                + "hh:mm am/pm hh:mm am/pm"
            )
            end_complete = False
            start_complete = False
            continue

        # If both datetime objects were successfully created, they get appended to the list and exits the while loop
        if start_complete and end_complete:
            print("Both time objects created")
            time_range = True
            event_array.append(start_time)
            event_array.append(end_time)

        # If both objects were unsuccessfully created, the bot notifies the user and the loop starts again
        else:
            await channel.send(
                "Make sure you follow this format(Start is first, end is second): mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
            )
            time_array = []
            msg_content = ""

    # Tries to create an Event_type object from the user input
    try:

        current = event_type(event_array[0], event_array[1], event_array[2])

        # Creates ScheduleBot directory in users Documents folder if it doesn't exist
        create_type_directory()

        filename = str(ctx.author.id) + 'event_types'

        # Checks if the calendar csv file exists, and creates it if it doesn't
        create_type_file(str(ctx.author.id))

        key = load_key(str(ctx.author.id))
        decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv")

        # Opens the current user's csv calendar file
        with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "r"
        ) as calendar_lines:
            calendar_lines = csv.reader(calendar_lines, delimiter=",")
            fields = next(calendar_lines)  # The column headers will always be the first line of the csv file
            rows = []
            line_number = 0
            flag = 0
            # Stores the current row in an array of rows if the row is not a new-line character
            # This check prevents an accidental empty lines from being kept in the updated file
            for line in calendar_lines:

                if len(line) > 0:

                    # If the file already has the same event type then inform user and exit loop
                    if line[0] == current.event_name:
                        flag = 1
                        if str(line[1]) == current.get_start_time() and str(line[2]) == current.get_end_time():
                            rows.append(line)
                            line_number = line_number + 1
                            await channel.send("Event type: " + str(line[0]) + " already exists in the given time range")
                            continue
                        await channel.send("Event type: " + str(
                            line[0]) + " already exist.\n Existing time range for this event type is " + str(
                            line[1]) + " " + str(line[
                                                     2]) + "\n The new time range entered now is " + current.get_start_time() + " " + current.get_end_time() + ". \n Please type 'change' for updating the time range or 'exit' for keeping existing time range.")
                        # Waits for user input
                        event_msg = await client.wait_for("message", check=check)
                        # Strips message to just the text the user entered
                        msg_content = event_msg.content
                        if msg_content == 'change':
                            rows.append(current.to_list_event())
                            await channel.send("The time range for your event was successfully updated!")
                            line_number = line_number + 1
                        elif msg_content == 'exit':
                            rows.append(line)
                            continue
                        else:
                            await channel.send("Invalid input, Time range is not changed.")
                            rows.append(line)
                            continue
                    else:
                        rows.append(line)
                        line_number = line_number + 1

            # If this is a new even type then append it to rows
            if flag == 0:
                rows.append(current.to_list_event())
                line_number = line_number + 1
                await channel.send("Your event was successfully created!")

        # Open current user's calendar file for writing
        with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "w", newline=""
        ) as calendar_file:
            # Write to column headers and array of rows back to the calendar file
            csvwriter = csv.writer(calendar_file)
            csvwriter.writerow(fields)
            if line_number > 1:
                csvwriter.writerows(rows)
            elif line_number == 1:
                csvwriter.writerow(rows[0])

        key = load_key(str(ctx.author.id))
        encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv")

        return True

    except Exception as e:
        # Outputs an error message if the event type could not be created
        print(e)
        TracebackType.print_exc()
        await channel.send(
            "There was an error while adding this event type. Make sure your formatting is correct and try creating the event type again."
        )
        return False
