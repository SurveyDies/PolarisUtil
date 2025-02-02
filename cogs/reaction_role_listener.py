import discord
from discord.ext import commands


class ReactionRoleListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager

    async def _get_reaction_role(self, payload):
        """Helper to fetch the role for a reaction using DataManager."""
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        message_id = str(payload.message_id)
        emoji = payload.emoji.name

        reaction_roles = self.dm.get_reaction_roles(guild_id, channel_id, message_id)
        return reaction_roles.get(emoji)

    async def _assign_role(self, member, role):
        """Helper to assign a role to a member."""
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            await member.send(
                f"I don't have permission to assign the role `{role.name}`. Please notify an admin.",
                delete_after=10,
            )

    async def _remove_role(self, member, role):
        """Helper to remove a role from a member."""
        try:
            await member.remove_roles(role)
        except discord.Forbidden:
            await member.send(
                f"I don't have permission to remove the role `{role.name}`. Please notify an admin.",
                delete_after=10,
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle adding reaction roles."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role_id = await self._get_reaction_role(payload)
        if role_id:
            role = guild.get_role(role_id)
            if role:
                member = guild.get_member(payload.user_id)
                if member and member != guild.me:
                    await self._assign_role(member, role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle removing reaction roles."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role_id = await self._get_reaction_role(payload)
        if role_id:
            role = guild.get_role(role_id)
            if role:
                member = guild.get_member(payload.user_id)
                if member and member != guild.me:
                    await self._remove_role(member, role)


async def setup(bot):
    await bot.add_cog(ReactionRoleListener(bot))
