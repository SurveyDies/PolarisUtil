from discord import app_commands
from discord.ext import commands


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="message", description="Sends a message via the bot")
    async def create_reaction_message(self, ctx, message: str):
        """Create a reaction message to assign roles."""

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send(
                "You don't have the necessary permissions to use this command.",
                ephemeral=True,
            )
            return

        msg = await ctx.send(message)

        await ctx.send(f"Message ID: `{msg.id}`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Message(bot))
