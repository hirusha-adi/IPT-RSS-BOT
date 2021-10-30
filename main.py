import os
import json
import asyncio
import platform
import discord
from discord.ext import commands
import feedparser
from keep_alive import keep_alive
from datetime import datetime


# //////////////////////////////////////////////////////////

configfile = json.load(open("config.json", "r", encoding="utf-8"))

# Bot token
TOKEN = configfile["TOKEN"]

# Bot prefix
MBOT_PREFIX = configfile["MBOT_PREFIX"]

# IPTorrents RSS Feed link
FEED_URL = configfile["FEED_URL"]

# Channel id in which you need to send the updates
SECRET_MOVIE_CHANNEL = int(configfile["SECRET_MOVIE_CHANNEL"])

# Channel id in which you need to send the log of updates
# (Trust me this is usefull)
SECRET_MOVIE_LOG_CHANNEL = int(configfile["SECRET_MOVIE_LOG_CHANNEL"])

# What is the delay of sending the request? (in seconds)
WAIT_SECONDS = int(configfile["WAIT_SECONDS"])

# Owner ID - only this person can use the commands
ALL_SECRET_OWNERS = []
ALL_SECRET_OWNERS_JSON = str(configfile["USABLE_PEOPLE"])
for SECRET_USER in ALL_SECRET_OWNERS_JSON.split(","):
    ALL_SECRET_OWNERS.append(int(SECRET_USER))


# //////////////////////////////////////////////////////////


client = commands.Bot(command_prefix=MBOT_PREFIX)


@client.event
async def on_ready():
    print(f"Python Version: {platform.python_version()}")
    print(f"Discord.py API Version: {discord.__version__}")
    print(f"Logged in as {client.user.name} | {client.user.id}")
    print(f"Bot is ready to be used!")

    # Usefull channels
    # Taken from ID's given above
    music_channel = client.get_channel(SECRET_MOVIE_CHANNEL)
    music_log_channel = client.get_channel(SECRET_MOVIE_LOG_CHANNEL)

    # Online Notice
    await music_log_channel.send(f""" **+ BOT ONLINE!** - {datetime.now()} - Bot Prefix: `{MBOT_PREFIX}` - Request Send Time: *{WAIT_SECONDS}* Seconds """)

    while True:
        try:
            # Feedparser is real helpful here
            blog_feed = feedparser.parse(FEED_URL)

            # Get the title of the current video at top
            TITLE = blog_feed.entries[0].title

            #  If the current title is same as the last title recieved
            # (stored in old.txt) btw
            # This will be skipped and will be tried again in the next round
            try:
                with open("old.txt", "r", encoding="utf-8") as old_file:
                    OLD_TITLE = old_file.read()
            except:
                OLD_TITLE = "NO FILE FOUND"

            if TITLE == OLD_TITLE:
                await music_log_channel.send(f"""**- Info:** RSS Feed not updated yet.""")

            # If the above check is false
            else:
                with open("old.txt", "w", encoding="utf-8") as new_file:
                    new_file.write(TITLE)

                LINK = blog_feed.entries[0].link
                PUB_DATE = blog_feed.entries[0].published
                SUMMARY = blog_feed.entries[0].summary
                print("-"*25)
                print("Title:", TITLE)
                print("Link:", LINK)
                print("Published Date:", PUB_DATE)
                print("Summary:", SUMMARY)

                embed = discord.Embed(
                    title=f"""{TITLE}""", color=0x00ff00)
                embed.set_author(name=f"{client.user.name}",
                                 icon_url=f"{client.user.avatar_url}")
                embed.add_field(
                    name="Title", value=f"""{TITLE}""", inline=False)
                embed.add_field(
                    name="Link", value=f"""{LINK}""", inline=False)
                embed.add_field(name="Published on",
                                value=f"""{PUB_DATE}""", inline=False)
                embed.add_field(name="Decription",
                                value=f"""{SUMMARY}""", inline=False)
                await music_channel.send(embed=embed)
                await music_log_channel.send(f"""**+ Success:** Sent *{TITLE}*""")

        except Exception as e:
            # If this happens....
            # DAMN! something is really wrong
            await music_log_channel.send(f"""**- Error:** {e}""")

        await asyncio.sleep(WAIT_SECONDS)


@client.command(help="use this command to find out what is wrong",
                breif="use this command to find out what is wrong")
async def test_if_broken(ctx):
    blog_feed = feedparser.parse(FEED_URL)
    print(blog_feed.entries)
    try:
        await ctx.send("**Here is the first element of the list:**")
        await ctx.send(f"""{blog_feed.entries[0]}""")
    except:
        await ctx.send("**- Unable** to send the first element of the list. check the console for more information")


@client.event
async def on_message(message):
    if client.user == message.author:
        return

    if message.author.id in ALL_SECRET_OWNERS:
        await client.process_commands(message)

keep_alive()
client.run(TOKEN)
