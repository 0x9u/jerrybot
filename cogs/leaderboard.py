import discord
from discord.ext import commands
from discord import app_commands
import database
from utils.generate import (
    generate_global_leaderboard,
    generate_guild_leaderboard,
    generate_coins_leaderboard,
    generate_slaves_leaderboard,
)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard", description="Display the global leaderboard."
    )
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        leaderboard = await database.db.get_leaderboard()
        await interaction.followup.send(
            embed=await generate_global_leaderboard(self.bot, leaderboard)
        )

    @app_commands.command(
        name="leaderboard_guild", description="Display the guild leaderboard."
    )
    async def leaderboard_guild(self, interaction: discord.Interaction):
        await interaction.response.defer()
        leaderboard = await database.db.get_leaderboard_guild(interaction.guild.id)
        await interaction.followup.send(
            embed=await generate_guild_leaderboard(
                self.bot, leaderboard, interaction.guild.name
            )
        )

    @app_commands.command(name="rich", description="Display the coins leaderboard.")
    async def rich(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_id = str(self.bot.user.id)
        leaderboard = await database.db.get_user_coins_leaderboard(bot_id)
        await interaction.followup.send(
            embed=await generate_coins_leaderboard(self.bot, leaderboard)
        )

    @app_commands.command(
        name="leaderboard_slaves", description="Display the slaves leaderboard."
    )
    async def slaves(self, interaction: discord.Interaction):
        await interaction.response.defer()
        leaderboard = await database.db.get_user_slaves_leaderboard()
        await interaction.followup.send(
            embed=await generate_slaves_leaderboard(self.bot, leaderboard)
        )


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
