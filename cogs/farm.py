import discord
from discord.ext import commands
from discord import app_commands
import database
from datetime import datetime, timezone, timedelta
from utils import seed_to_plants
import asyncio

from views import PaginationView


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    farm_group = app_commands.Group(name="farm", description="Farm commands.")

    @farm_group.command(name="check", description="Display the farm.")
    async def check(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)

        crops = await database.db.get_farm_crops(user_id)
        data = []
        for crop in crops:
            time = datetime.fromisoformat(crop["time_planted"])
            time_elapsed = datetime.now(timezone.utc) - time
            time = (
                timedelta(minutes=30) - time_elapsed
                if timedelta(minutes=30) - time_elapsed > timedelta(0)
                else timedelta(0)
            )
            data.append(
                {
                    "name": crop["items"]["name"],
                    "value": f"Time left: {int(time.total_seconds() // 60)}:{int(time.total_seconds() % 60)}",
                }
            )

        view = await PaginationView.create(
            data, "Farm", "Crops you currently have growing.", interaction
        )
        await view.wait()

    @farm_group.command(name="harvest", description="Harvest crops.")
    async def harvest(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        crops = await database.db.harvest_farm(user_id)
        plants = await asyncio.gather(*[seed_to_plants(crop) for crop in crops])

        for plant in plants:
            await database.db.add_item_to_inventory(user_id, plant, 1)

        if not crops:
            await interaction.followup.send("You have no crops to harvest.")
            return

        await interaction.followup.send("Crops harvested!")


async def setup(bot):
    await bot.add_cog(Farm(bot))
