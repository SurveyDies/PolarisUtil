import discord
from discord.ext import commands, tasks

class ReactionRoleTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reaction_messages.start()
        
    def cog_unload(self):
        """Stops the task when the cog is unloaded."""
        self.check_reaction_messages.cancel()

    @tasks.loop(seconds=3)
    async def check_reaction_messages(self):
        """Check if the messages for reactions still exist and delete the association in the data file."""
        for guild_id, guild_data in list(self.bot.reaction_role_map.items()):
            guild = await self.bot.fetch_guild(int(guild_id))
            if not guild:
                continue

            for channel_id, channel_data in list(guild_data.items()):
                channel = guild.get_channel(int(channel_id))
                if not channel:
                    continue

                for message_id in list(channel_data.keys()):
                    try:
                        msg = await channel.fetch_message(int(message_id))
                    except discord.NotFound:
                        del self.bot.reaction_role_map[guild_id][channel_id][message_id]
                        self.bot.save_data()
                    except discord.Forbidden:
                        print(f"Missing permissions to fetch message {message_id} in channel {channel_id}.")
                    except discord.HTTPException as e:
                        print(f"Error fetching message {message_id}: {str(e)}")

                if not self.bot.reaction_role_map[guild_id][channel_id]:
                    del self.bot.reaction_role_map[guild_id][channel_id]

            if not self.bot.reaction_role_map[guild_id]:
                del self.bot.reaction_role_map[guild_id]

        self.bot.save_data()

    @check_reaction_messages.before_loop
    async def before_check_reaction_messages(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ReactionRoleTasks(bot))
