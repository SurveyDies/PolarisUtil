import os
import json
import discord
from discord.ext import commands
from discord import app_commands

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)
        self.start_time = None
        self.data_file = os.getenv("BOT_DATA_PATH", "bot_data.json")
        self.hold_messages_file = "hold_messages.json"
        self.held_threads = {}
        self.reaction_role_map = {}
        self.hold_messages = []

        self.load_data()

    def load_data(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    data = json.load(f)
                    self.held_threads = data.get("held_threads", {})
                    self.reaction_role_map = data.get("reaction_roles", {})
                except json.JSONDecodeError:
                    self.held_threads = {}
                    self.reaction_role_map = {}

        if os.path.exists(self.hold_messages_file):
            with open(self.hold_messages_file, "r", encoding='utf-8') as f:
                try:
                    hold_data = json.load(f)
                    self.hold_messages = hold_data.get("messages", [])
                except json.JSONDecodeError:
                    print("Error loading hold messages file. Using default list.")

                    self.hold_messages = ["held!"]
        else:
            print(f"Hold messages file '{self.hold_messages_file}' not found. Using default list.")
            self.hold_messages = ["held!"]

    def save_data(self):
        """General method to save any data to the data file."""
        data = {
            "held_threads": self.held_threads,
            "reaction_roles": self.reaction_role_map
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    async def setup_hook(self):
        cog_files = ['cogs.tasks.check_threads', 'cogs.tasks.check_reaction_messages', 'cogs.add_role', 'cogs.help', 'cogs.info', 'cogs.message', 'cogs.reaction_roles', 'cogs.remove_role', 'cogs.thread_hold']
        
        for cog in cog_files:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}!")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        
        await self.tree.sync()
