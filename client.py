import os
import discord
from discord.ext import commands

from dataManager import DataManager


class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="", intents=intents)
        self.start_time = None
        self.data_file = os.getenv("BOT_DATA_PATH", "bot_data.json")
        self.data_manager = DataManager(self.data_file)

    async def setup_hook(self):
        cog_files = [
            "cogs.tasks.check_threads",
            "cogs.tasks.data_cleanup",
            "cogs.help",
            "cogs.info",
            "cogs.message",
            "cogs.reaction_role_listener",
            "cogs.reaction_roles",
            "cogs.setup_voice_hub",
            "cogs.thread_hold",
            "cogs.voice",
        ]

        for cog in cog_files:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}!")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")

        await self.tree.sync()
