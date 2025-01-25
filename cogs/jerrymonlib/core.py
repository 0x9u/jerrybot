from discord.ext import commands
from discord import app_commands

# Category
# type 1  = Attack
# type 2  = Special
# type 3  = Status

# Type (Attack and Special)
# type 1  = Physical
# type 2  = Gun
# type 3  = Carrot
# type 4  = Rabbit

# Type (Status)
# type 1 = Poison
# type 2 = Heal
# type 3 = Stun
# type 4 = Speed
# type 5 = Attack
# type 6 = Defense

# todo: figure out how to make moves 

# todo: implement status condition, captured at, nickname
# todo: implement leveling up

class JerryMonCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_hunt_time : dict[str, int] = {}
    
    jerrymon_group = app_commands.Group(name="jerrymon", description="Jerrymon commands.")
