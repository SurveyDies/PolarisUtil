import os
import json
import random
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta


class ThreadTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager
        self.hold_messages_file = "hold_messages.json"
        self.hold_messages = {}
        self.load_messages()

        self.check_held_threads.start()

    def load_messages(self):
        if os.path.exists(self.hold_messages_file):
            with open(self.hold_messages_file, "r", encoding="utf-8") as f:
                try:
                    hold_data = json.load(f)
                    self.hold_messages = hold_data.get("messages", [])
                except json.JSONDecodeError:
                    print("Error loading hold messages file. Using default list.")
                    self.hold_messages = ["held!"]
        else:
            self.hold_messages = ["held!"]

    def cog_unload(self):
        self.check_held_threads.cancel()

    @tasks.loop(seconds=4)
    async def check_held_threads(self):
        """Check threads in held guilds and send messages to keep them active."""
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(seconds=3)

        for guild_id in list(self.dm.get_held_threads().keys()):
            guild = await self.bot.fetch_guild(int(guild_id))
            if not guild:
                continue

            for thread_id in self.dm.get_held_threads(guild_id)[:]:
                thread = self.bot.get_channel(int(thread_id))
                if not thread or thread.archived:
                    continue

                if thread.last_message_id:
                    last_message = await thread.fetch_message(thread.last_message_id)
                    if last_message.created_at < threshold:
                        await thread.send(random.choice(self.hold_messages))

    @check_held_threads.before_loop
    async def before_check_held_threads(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ThreadTasks(bot))
