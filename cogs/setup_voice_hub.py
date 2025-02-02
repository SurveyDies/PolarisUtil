import discord
from discord import app_commands
from discord.ext import commands


class SetupVoiceHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm = self.bot.data_manager

    group = app_commands.Group(name="setup", description="Commands pertaining to setup")

    @group.command(
        name="voice_hub",
        description="Creates a hub voice channel for temporary voice channels.",
    )
    async def setup_voice_hub(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True, speak=True),
            guild.me: discord.PermissionOverwrite(
                manage_channels=True, move_members=True
            ),
        }
        if "hub_channel_id" in self.dm.get_temp_channels(str(guild.id)):
            await interaction.response.send_message(
                "You already have a voice hub set up!"
            )
            return

        category = discord.utils.get(guild.categories, name="Temporary Voice")
        if category is None:
            category = await guild.create_category("Temporary Voice")

        hub_channel = await guild.create_voice_channel(
            "Join to Create 🔊", category=category, overwrites=overwrites
        )

        self.dm.setup_voice_hub(guild.id, hub_channel.id)

        await interaction.response.send_message(
            f"Temporary voice setup complete! Users can join {hub_channel.mention} to create their own voice channels.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        guild = member.guild
        temp_channels = self.dm.get_temp_channels(str(guild.id))
        if not temp_channels or not self.dm.get_guild_voice_hub(str(guild.id)):
            return

        if after.channel and after.channel.id == self.dm.get_guild_voice_hub(guild.id):
            category = after.channel.category
            temp_channel = await guild.create_voice_channel(
                f"{member.display_name}'s Channel", category=category
            )

            await member.move_to(temp_channel)

            self.dm.add_temp_channel(guild.id, temp_channel.id, member.id)

            await temp_channel.send(
                f"Welcome, {member.mention}! This is your temporary voice channel. Feel free to chat!"
            )

        if before.channel and self.dm.get_channel_data(guild.id, before.channel.id):
            if len(before.channel.members) == 0:
                self.dm.remove_temp_channel(guild.id, before.channel.id)

                await before.channel.delete()


async def setup(bot):
    await bot.add_cog(SetupVoiceHub(bot))
