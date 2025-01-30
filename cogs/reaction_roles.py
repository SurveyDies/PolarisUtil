import discord
from discord.ext import commands

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        if str(channel_id) in self.bot.reaction_role_map.get(guild_id, {}):
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            role_id = self.bot.reaction_role_map[guild_id][channel_id].get(str(payload.message_id), {}).get(payload.emoji.name)
            if role_id:
                role = guild.get_role(role_id)
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and member != guild.me:
                        try:
                            await member.add_roles(role)
                        except discord.Forbidden:
                            await member.send(
                                f"I don't have permission to assign the role `{role.name}`. Please notify an admin.",
                                delete_after=10
                            )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        if str(channel_id) in self.bot.reaction_role_map.get(guild_id, {}):
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            role_id = self.bot.reaction_role_map[guild_id][channel_id].get(str(payload.message_id), {}).get(payload.emoji.name)
            if role_id:
                role = guild.get_role(role_id)
                if role:
                    member = guild.get_member(payload.user_id)
                    if member and member != guild.me:
                        try:
                            await member.remove_roles(role)
                        except discord.Forbidden:
                            await member.send(
                                f"I don't have permission to remove the role `{role.name}`. Please notify an admin.",
                                delete_after=10
                            )

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
