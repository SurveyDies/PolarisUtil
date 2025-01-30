import discord
from discord import app_commands
from discord.ext import commands

class AddRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_role", description="Add a role to a reaction role message.")
    async def add_role(self, interaction: discord.Interaction, message_id: str, role: discord.Role, emoji: str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You don't have the necessary permissions to use this command.", ephemeral=True
            )
            return

        try:
            msg = await interaction.channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message("Message not found!", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "I don't have permission to manage roles. Please grant me the necessary permissions.", ephemeral=True
            )
            return

        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message(
                f"I cannot assign the role `{role.name}` because it's higher than my highest role.",
                ephemeral=True,
            )
            return
        
        if role.managed:
            await interaction.response.send_message(
                f"I cannot assign the role `{role.name}` because it is externally managed.",
                ephemeral=True,
            )
            return

        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)

        self.bot.reaction_role_map.setdefault(guild_id, {}).setdefault(channel_id, {}).setdefault(message_id, {})

        self.bot.reaction_role_map[guild_id][channel_id][message_id][emoji] = role.id
        self.bot.save_data()

        if not interaction.guild.me.guild_permissions.add_reactions:
            await interaction.response.send_message(
                f"I cannot add the reaction `{emoji}` because I don't have permission to add reactions. "
                f"The role `{role.name}` has been mapped to `{emoji}` but you will need to manually add the reaction to the message.",
                ephemeral=True,
            )
            return

        try:
            await msg.add_reaction(emoji)
            await interaction.response.send_message(
                f"Added role `{role.name}` with emoji `{emoji}` to message `{message_id}`.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"I could not add the reaction `{emoji}` to the message. Please ensure I have permission to do so.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"An error occurred while trying to add the reaction: {str(e)}", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AddRole(bot))
