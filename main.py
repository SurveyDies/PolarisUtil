import os

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

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    client.start_time = datetime.utcnow()
    await client.change_presence(activity=discord.CustomActivity(name="Assisting Dumbasses"))
    
client.run(os.getenv("CLIENT_SECRET"))