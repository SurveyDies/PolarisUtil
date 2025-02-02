import os
import configparser

import discord
from datetime import datetime

from client import MyClient

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True
intents.message_content = True

client = MyClient(intents=intents)

CONFIG_FILE = 'config.ini'

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    client.start_time = datetime.utcnow()
    await client.change_presence(
        activity=discord.CustomActivity(name="Making bad decisions look easy")
    )

def main():
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Please make a copy of 'config.TEMPLATE.ini', and rename it to 'config.ini'")
    else:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        try:
            bot_token = config["DEFAULT"]["bot_token"]
        except KeyError:
            print("Bot token not found in the config file. Please ensure it is added.")
            return
        client.run(bot_token)

if __name__ == '__main__':
    main()
