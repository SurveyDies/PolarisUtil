import random
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta

class ThreadTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_held_threads.start()

    def cog_unload(self):
        """Stops the task when the cog is unloaded."""
        self.check_held_threads.cancel()

    @tasks.loop(seconds=4)
    async def check_held_threads(self):
        """Check threads in held guilds and send messages to keep them active."""
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(seconds=3)

        for guild_id in list(self.bot.held_threads.keys()):
            guild = await self.bot.fetch_guild(int(guild_id))
            if not guild:
                continue

            for thread_id in self.bot.held_threads.get(guild_id, [])[:]:
                thread = self.bot.get_channel(int(thread_id))
                if not thread or thread.archived:
                    continue

                if thread.last_message_id:
                    last_message = await thread.fetch_message(thread.last_message_id)
                    if last_message.created_at < threshold:
                        await thread.send(random.choice(self.bot.hold_messages))

    @check_held_threads.before_loop
    async def before_check_held_threads(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ThreadTasks(bot))
