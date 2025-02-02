import discord
from discord import app_commands
from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager

    group = app_commands.Group(
        name="voice", description="Commands pertaining to temporary voice channels"
    )

    def temp_channel_state(self, interaction: discord.Interaction):
        """Check if the user is in a temporary voice channel and return data."""
        try:
            return self.dm.get_channel_data(
                interaction.guild_id, interaction.user.voice.channel.id
            )
        except (AttributeError, KeyError) as e:
            assert LookupError(f"Failed to check voice state of user: {e}")
            return None

    async def valid_env(self, interaction: discord.Interaction):
        """Check if the user is in a valid temporary voice channel."""
        if not (channel_state := self.temp_channel_state(interaction)):
            await interaction.response.send_message(
                "You can only run this command in a temporary voice channel.",
                ephemeral=True,
            )
            return None
        return channel_state

    async def check_owner(self, interaction: discord.Interaction, channel_state):
        """Helper method to check if the user is the owner of the channel."""
        if channel_state["owner_id"] != interaction.user.id:
            await interaction.response.send_message(
                "You do not own this channel.", ephemeral=True
            )
            return False
        return True

    @group.command(name="lock", description="Locks VC")
    async def voice_lock_command(self, interaction: discord.Interaction):
        """Lock a temporary voice channel."""
        if not (channel_state := await self.valid_env(interaction)):
            return

        if not await self.check_owner(interaction, channel_state):
            return

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role, connect=False
        )
        await interaction.response.send_message(
            f"Channel `{interaction.channel.name}` is now locked.", ephemeral=True
        )

    @group.command(name="unlock", description="Unlocks VC")
    async def voice_unlock_command(self, interaction: discord.Interaction):
        """Unlock a temporary voice channel."""
        if not (channel_state := await self.valid_env(interaction)):
            return

        if not await self.check_owner(interaction, channel_state):
            return

        await interaction.user.voice.channel.set_permissions(
            interaction.guild.default_role, connect=True
        )
        await interaction.response.send_message(
            f"Channel `{interaction.channel.name}` is now unlocked.", ephemeral=True
        )

    @group.command(name="permit", description="Allows the user to join the channel")
    async def voice_permit_command(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Permit a user to join the channel."""
        if not (channel_state := await self.valid_env(interaction)):
            return

        if not await self.check_owner(interaction, channel_state):
            return

        await interaction.user.voice.channel.set_permissions(user, connect=True)
        await interaction.response.send_message(
            f"Permitted `{user}` to join the channel.", ephemeral=True
        )

    @group.command(name="reject", description="Rejects a user from joining a channel")
    async def voice_reject_command(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Reject a user from joining the channel."""
        if not (channel_state := await self.valid_env(interaction)):
            return

        if not await self.check_owner(interaction, channel_state):
            return

        await interaction.user.voice.channel.set_permissions(user, connect=False)
        await interaction.response.send_message(
            f"Rejected `{user}` from joining the channel.", ephemeral=True
        )

    @group.command(
        name="claim",
        description="Allows user to claim VC if the previous owner has left",
    )
    async def voice_claim_command(self, interaction: discord.Interaction):
        """Claim a temporary voice channel if the owner has left."""
        if not (channel_state := await self.valid_env(interaction)):
            return

        current_owner = channel_state.get("owner_id")

        if current_owner and current_owner != interaction.user.id:
            channel = interaction.user.voice.channel
            if current_owner not in [member.id for member in channel.members]:
                self.dm.set_channel_owner(
                    interaction.guild_id, channel.id, interaction.user.id
                )
                await interaction.response.send_message(
                    "You have successfully claimed the channel.", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "This channel already has an owner. You can only claim it if the owner has left.",
                    ephemeral=True,
                )
        elif current_owner == interaction.user.id:
            await interaction.response.send_message(
                "You are already the owner of this voice channel.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Voice(bot))
