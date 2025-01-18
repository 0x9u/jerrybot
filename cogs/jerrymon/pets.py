import discord
from discord import app_commands
import database

from .core import JerryMonCore, jerrymon_group

class JerryMonPets(JerryMonCore):
    @jerrymon_group.command(name="list", description="List jerrymon you currently have on you.")
    async def list(self, interaction: discord.Interaction):
        pass

    @jerrymon_group.command(name="box", description="List jerrymon in storage.")
    async def box(self, interaction: discord.Interaction):
        pass
    
    @jerrymon_group.command(name="nickname", description="Nickname your jerry.")
    async def nickname(self, interaction: discord.Interaction):
        pass

    @jerrymon_group.command(name="abandon", description="Abandon your jerry.")
    async def abandon(self, interaction: discord.Interaction):
        pass

    @jerrymon_group.command(name="info", description="Get information on a jerrymon.")
    async def info(self, interaction: discord.Interaction):
        pass

    @jerrymon_group.command(name="give", description="Give your jerrymon to another player.")
    @app_commands.describe(user="User you want to give jerrymon to.", jerrymon_id="Id of jerrymon.")
    async def info(self, interaction: discord.Integration, user: discord.User, jerrymon_id: int):
        pass