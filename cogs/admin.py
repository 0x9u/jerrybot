import discord
from discord.ext import commands
from discord import app_commands

import database

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="add_allowed_channel", description="Add a channel to the allowed channels list.")
    async def add_allowed_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        guild_id = str(interaction.guild_id)
        channel_id = str(channel.id)

        if await database.db.get_allowed_channel(guild_id, channel_id):
            await interaction.followup.send(f"{channel.mention} is already in the allowed channels list.")
            return
        
        await database.db.add_allowed_channel(guild_id, channel_id)
        await interaction.followup.send(f"{channel.mention} has been added to the allowed channels list.")
    
    @app_commands.command(name="remove_allowed_channel", description="Remove a channel from the allowed channels list.")
    async def remove_allowed_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        guild_id = str(interaction.guild_id)
        channel_id = str(channel.id)

        if not await database.db.get_allowed_channel(guild_id, channel_id):
            await interaction.followup.send(f"{channel.mention} is not in the allowed channels list.")
            return
        
        await database.db.remove_allowed_channel(guild_id, channel_id)
        await interaction.followup.send(f"{channel.mention} has been removed from the allowed channels list.")

async def setup(bot):
    await bot.add_cog(Admin(bot))