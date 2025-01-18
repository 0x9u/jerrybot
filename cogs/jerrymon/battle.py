import discord
from discord import app_commands
import database

from .core import JerryMonCore, jerrymon_group

class JerryMonBattle(JerryMonCore):
    @jerrymon_group.command(name="battle", description="Battle other jerrymon")
    @app_commands.describe(user="User you wanna battle with.")
    async def battle(self, interaction: discord.Interaction, user: discord.User):
        pass

    @jerrymon_group.command(name="hunt", description="Hunt for jerrymon.")
    async def hunt(self, interaction: discord.Interaction):
        pass
