import discord
from discord import app_commands
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager

    group = app_commands.Group(name="role", description="Commands pertaining to Reaction roles")

    @group.command(
        name="add", description="Add a role to a reaction role message."
    )
    async def add_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        role: discord.Role,
        emoji: str,
    ):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You don't have the necessary permissions to use this command.",
                ephemeral=True,
            )
            return

        try:
            msg = await interaction.channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message(
                "Message not found!", ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "I don't have permission to manage roles. Please grant me the necessary permissions.",
                ephemeral=True,
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

        self.dm.add_reaction_role(guild_id, channel_id, message_id, emoji, role.id)

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
                f"An error occurred while trying to add the reaction: {str(e)}",
                ephemeral=True,
            )

    @group.command(
        name="remove", description="Removes a reaction role from a message."
    )
    async def remove_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        remove_members: bool = False,
    ):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You don't have the necessary permissions to use this command.",
                ephemeral=True,
            )
            return

        try:
            msg = await interaction.channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message(
                "Message not found!", ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)

        if emoji not in self.dm.get_reaction_roles(guild_id, channel_id, message_id):
            await interaction.response.send_message(
                "No role is assigned to this emoji on the specified message.",
                ephemeral=True,
            )
            return

        role_id = self.dm.remove_reaction_role(guild_id, channel_id, message_id, emoji)

        await interaction.response.defer(ephemeral=True)

        if remove_members:
            role = interaction.guild.get_role(role_id)
            if role is None:
                await interaction.response.send_message(
                    "The role associated with this reaction no longer exists.",
                    ephemeral=True,
                )
                return

            removed_count = 0
            for reaction in msg.reactions:
                if str(reaction.emoji) == emoji:
                    async for user in reaction.users():
                        if not user.bot:
                            member = interaction.guild.get_member(
                                user.id
                            ) or await interaction.guild.fetch_member(user.id)
                            if member is None:
                                continue

                            try:
                                await member.remove_roles(role)
                                removed_count += 1
                            except discord.Forbidden:
                                print(
                                    f"Missing permissions to remove {role.name} from {member.display_name}"
                                )
                            except discord.HTTPException as e:
                                print(f"Failed to remove role {role.name}: {e}")

            await interaction.followup.send(
                f"Removed `{role.name}` from `{removed_count}` users who reacted with `{emoji}`."
                if removed_count > 0
                else f"No users had the `{role.name}` role.",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"Removed role association for `{emoji}` from message `{message_id}`.",
                ephemeral=True,
            )

        try:
            await msg.clear_reaction(emoji)
        except discord.Forbidden:
            await interaction.followup.send(
                "I do not have permission to remove reactions from this message.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"An error occurred while removing the reaction: {str(e)}",
                ephemeral=True,
            )
        return

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))