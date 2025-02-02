import discord
from discord import app_commands
from discord.ext import commands


class RemoveRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager

    @app_commands.command(
        name="remove_role", description="Removes a reaction role from a message."
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
    await bot.add_cog(RemoveRole(bot))
