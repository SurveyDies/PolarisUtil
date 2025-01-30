from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Provides help information.")
    async def help_command(self, ctx):
        await ctx.response.send_message(f"Hi, {ctx.user.mention}")

async def setup(bot):
    await bot.add_cog(Help(bot))
