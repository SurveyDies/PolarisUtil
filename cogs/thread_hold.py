import discord
from discord import app_commands
from discord.ext import commands

class Hold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hold", description="Toggle holding this thread open.")
    async def hold_command(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_threads:
            await interaction.response.send_message(
                "You don't have the necessary permissions to use this command.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message(
                "This command is only for threads!", ephemeral=True
            )
            return

        guild_id = str(interaction.guild_id)
        thread_id = str(interaction.channel.id)

        if guild_id not in self.bot.held_threads:
            self.bot.held_threads[guild_id] = []

        if thread_id not in self.bot.held_threads[guild_id]:
            self.bot.held_threads[guild_id].append(thread_id)
            await interaction.response.send_message(
                f"Now holding thread: {interaction.channel.name}", ephemeral=True
            )
        else:
            self.bot.held_threads[guild_id].remove(thread_id)
            if not self.bot.held_threads[guild_id]:
                del self.bot.held_threads[guild_id]
            await interaction.response.send_message(
                f"No longer holding thread: {interaction.channel.name}", ephemeral=True
            )

        self.bot.save_data()

async def setup(bot):
    await bot.add_cog(Hold(bot))
