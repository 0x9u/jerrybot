import discord
from discord.ext import commands
from discord import app_commands
import database
import time
import datetime

SLAVE_RATE = 10
FARM_RATE = 5_000
MINES_RATE = 100_000
TIME_TO_COLLECT = 30 * 60


class Tycoon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # user id to last collected time
        self.last_collected: dict[str, int] = {}

    @app_commands.command(name="tycoon", description="Display the tycoon.")
    async def tycoon(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        user_id = str(interaction.user.id if user is None else user.id)

        await database.db.verify_user(user_id)

        slaves = await database.db.get_slaves(user_id)
        farms = await database.db.get_farms(user_id)
        mines = await database.db.get_mines(user_id)

        embed = discord.Embed(
            title="Tycoon",
            description=f"The tycoon of {(interaction.user if user is None else user).name}",
        )

        embed.add_field(
            name="Slaves",
            value=f"Slaves: {slaves} - rate {SLAVE_RATE * slaves} per 30 minutes",
            inline=False,
        )
        embed.add_field(
            name="Farms",
            value=f"Farms: {farms} - rate {FARM_RATE * farms} per 30 minutes",
            inline=False,
        )
        embed.add_field(
            name="Mines",
            value=f"Mines: {mines} - rate {MINES_RATE * mines} per 30 minutes",
            inline=False,
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="collect", description="Collect coins from the tycoon.")
    async def collect(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)

        await database.db.verify_user(user_id)

        slaves = await database.db.get_slaves(user_id)
        farms = await database.db.get_farms(user_id)
        mines = await database.db.get_mines(user_id)

        if slaves == 0 and farms == 0 and mines == 0:
            embed = discord.Embed(
                title="Bruh",
                description="You have nothing in ur tycoon.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        last_collected = self.last_collected.get(user_id, 0)

        current_time = time.time()

        time_diff = round(current_time - last_collected)

        if time_diff > TIME_TO_COLLECT:
            self.last_collected[user_id] = current_time

            buff = await database.db.get_buff(user_id)
            expired = False

            if buff:
                time_created = datetime.datetime.fromisoformat(
                    buff[0]["time_created"].replace("Z", "+00:00")
                )
                if time_created + datetime.timedelta(hours=2) < datetime.datetime.now(
                    datetime.timezone.utc
                ):
                    await database.db.delete_buff(user_id)
                    expired = True

            slave_multiplier = (
                buff[0]["slaves_multiplier"] if buff and not expired else 1
            )

            coins = (
                SLAVE_RATE * slaves * slave_multiplier
                + FARM_RATE * farms
                + MINES_RATE * mines
            )

            taxed = int(coins * 0.1)
            coins -= taxed

            await database.db.update_user_coins(user_id, coins)
            bot_id = str(self.bot.user.id)
            await database.db.update_user_coins(bot_id, taxed)

            await interaction.followup.send(
                f"Collected {coins} coins from the tycoon.\n10% of your coins got taxed: {taxed}"
            )
        else:
            await interaction.followup.send(
                f"Can't collect yet. Collect in {TIME_TO_COLLECT - time_diff} seconds."
            )

async def setup(bot):
    await bot.add_cog(Tycoon(bot))
