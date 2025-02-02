import random
import datetime

import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="info",
        description="Displays bot information and statistics with a bit of flair!",
    )
    async def info_command(self, ctx):
        bot_uptime = datetime.datetime.utcnow() - self.bot.start_time
        formatted_uptime = str(bot_uptime).split(".")[0]

        moods = [
            "Just vibing in the digital space.",
            "Running smoother than a cat on a Roomba.",
            "Busy assisting with all your requests!",
            "Forever learning, never stopping.",
            "Currently sipping on some data bytes.",
        ]
        bot_mood = random.choice(moods)

        embed = discord.Embed(
            title="🤖 Bot Information",
            description="Here’s some info about me!",
            color=discord.Color.blurple(),
        )

        embed.add_field(name="📅 Version", value="0.3.0", inline=False)
        embed.add_field(name="👨‍💻 Developer", value="@Surveydies", inline=False)
        embed.add_field(name="🌍 Release Year", value="2025", inline=False)
        embed.add_field(name="⏳ Uptime", value=formatted_uptime, inline=False)
        embed.add_field(
            name="🌐 Guilds I'm in", value=len(self.bot.guilds), inline=False
        )
        embed.add_field(
            name="👥 Users I'm serving",
            value=len(set(self.bot.get_all_members())),
            inline=False,
        )
        embed.add_field(
            name="💻 GitHub",
            value="[Check out my code on GitHub!](https://github.com/SurveyDies/PolarisUtil)",
            inline=False,
        )
        embed.add_field(name="🗨️ Bot Mood", value=bot_mood, inline=False)

        embed.set_footer(
            text=f"Requested by {ctx.user.name}", icon_url=ctx.user.avatar.url
        )

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
