import discord
from functionality.highlights import convert_to_12
from functionality.shared_functions import read_event_file, create_event_tree, delete_event_from_file


async def delete_event(ctx, arg):
    """
    Function:
        delete_event
    Description:
        A existing event is deleted from the user's schedule file
    Input:
        ctx: the current context
        arg: the instance of the bot
    Output:
        - A reply saying whether the event was deleted or not
    """
 
    channel = await ctx.author.create_dm()
    await channel.send(
                    "Enter the name of the event from the following to be deleted : "
                )
    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    # Open and read user's calendar file
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id))
    print(str(ctx.author.id))
    print("\n\n\n\n\n")

    # Initialize variables
    channel = await ctx.author.create_dm()
    event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': '', 'loc': ''}
    events = []
    eventFlag = False

    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
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
            # dates = [event['startDate'], event['endDate']]

            events.append(event)

            # reset event
            event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}

        # find all the existing schedules and display them
        if len(events) != 0:
            for e in events:
                embed = discord.Embed(colour=discord.Colour.magenta(), timestamp=ctx.message.created_at,
                              title="Your Schedule:")
                embed.set_footer(text=f"Requested by {ctx.author}")
                embed.add_field(name="Event Name:", value=e['name'], inline=False)
                embed.add_field(name="Start Time:", value=e['startTime'], inline=True)
                embed.add_field(name="End Time:", value=e['endTime'], inline=True)
                embed.add_field(name="Event Type:", value=e['type'], inline=False)
                #embed.add_field(name="Description:", value=e['desc'], inline=False)
                if 'location' in e.keys():
                    embed.add_field(name="Location:", value=e['location'], inline=False)
                else:
                    embed.add_field(name="Location:", value='None', inline=False)
                
                await channel.send(f"You have {e['name']} scheduled , from {e['startTime']} to {e['endTime']}")
                #await ctx.send(embed=embed)
        else:
            await channel.send("You don't have any event scheduled..!!")
    else:
        eventFlag = True
        await channel.send("Looks like your schedule is empty. You can add events using the '!schedule' command!")

    # delete the event and event type
    if not eventFlag:
        await channel.send("Please enter the name of the event you want to delete")
        event_msg = await arg.wait_for("message", check=check)  # Waits for user input
        event_msg = event_msg.content  # Strips message to just the text the user entered
        to_remove = []

        if len(events) != 0:
            # For every row in calendar file
            for e in events:
                # Get event details
                if e['name'].lower() == event_msg.lower():
                    to_remove.append(e)
                    print("Attempting to delete")
                    print("Row to be deleted " + e.__str__())
                    delete_event_from_file(str(ctx.author.id), e)
                    print("Deleted")
                    await channel.send(f"The event: {e['name']} was deleted..!!")
                else:
                    print("The entered event name does not exists..!! Please try again")
                    #await channel.send(
                    #"The entered event name does not exists..!! Please try again"
                    #)
