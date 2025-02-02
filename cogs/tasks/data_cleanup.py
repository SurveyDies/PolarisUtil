import discord
from discord.ext import commands, tasks


class DataCleanupTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager
        self.check_reaction_messages.start()
        self.check_voice_hubs.start()

    def cog_unload(self):
        """Stops the tasks when the cog is unloaded."""
        self.check_reaction_messages.cancel()
        self.check_voice_hubs.cancel()

    @tasks.loop(seconds=3)
    async def check_reaction_messages(self):
        """Check if the messages for reactions still exist and if not delete the association in the data file."""
        reaction_roles = self.dm.get_reaction_roles()

        for guild_id, guild_data in list(reaction_roles.items()):
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue

            for channel_id, channel_data in list(guild_data.items()):
                channel = guild.get_channel(int(channel_id))
                if not channel:
                    continue

                for message_id in list(channel_data.keys()):
                    try:
                        await channel.fetch_message(int(message_id))
                    except discord.NotFound:
                        self.dm.remove_reaction_role(guild_id, channel_id, message_id)
                    except discord.Forbidden:
                        print(
                            f"Missing permissions to fetch message {message_id} in channel {channel_id}."
                        )
                    except discord.HTTPException as e:
                        print(f"Error fetching message {message_id}: {str(e)}")

    @tasks.loop(seconds=10)
    async def check_voice_hubs(self):
        """Check if the stored voice hub channels still exist and remove invalid ones."""
        temp_channels = self.dm.get_temp_channels()

        for guild_id, guild_data in list(temp_channels.items()):
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue

            hub_channel_id = guild_data.get("hub_channel_id")
            if hub_channel_id:
                hub_channel = guild.get_channel(hub_channel_id)
                if not hub_channel:
                    self.dm.destroy_voice_hub(guild_id)

    @check_reaction_messages.before_loop
    async def before_check_reaction_messages(self):
        await self.bot.wait_until_ready()

    @check_voice_hubs.before_loop
    async def before_check_voice_hubs(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(DataCleanupTasks(bot))
