from discord.ext import commands
from discord import app_commands

class JerryMonCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

jerrymon_group = app_commands.Group(name="jerrymon", description="Jerrymon commands.")