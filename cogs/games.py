import discord
from discord.ext import commands
from discord import app_commands
import database
from utils import IntOrAll
from views import Connect4View
from shared import shared

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.in_game = set()
    

    @app_commands.command(name="connect4", description="Play a game of Connect 4.")
    async def connect4(self, interaction: discord.Interaction, user: discord.User, bet: str):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        target_id = str(user.id)

        await database.db.verify_user(user_id)
        await database.db.verify_user(target_id)

        if user_id == target_id:
            await interaction.followup.send("You can't play Connect 4 with yourself.")
            return
        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Bet must be an integer.")
            return
        
        bet = parsed_amount.value if parsed_amount.value != "all" else await database.db.get_user_coins(user_id)



        if await database.db.get_user_coins(user_id) < bet:
            await interaction.followup.send("You don't have enough coins to play Connect 4.")
            return
        
        if await database.db.get_user_coins(target_id) < bet:
            await interaction.followup.send(f"{user.name} doesn't have enough coins to play Connect 4.")
            return
        
        if user_id in self.in_game:
            await interaction.followup.send("You are already in a game.")
            return
        
        if target_id in self.in_game:
            await interaction.followup.send(f"{user.name} is already in a game.")
            return

        embed = discord.Embed(
            title="Connect 4",
            description=f"Play Connect 4 with {user.mention}.\nMoney betted on: {bet}",
        )

        shared.rob_lock.add(user_id)
        shared.rob_lock.add(target_id)

        self.in_game.add(user_id)
        self.in_game.add(target_id)

        message = await interaction.followup.send(embed=embed)

        view = Connect4View(user, interaction.user, embed, message)
        await message.edit(embed=embed, view=view)
        await view.wait()

        if view.winner == 1:
            await database.db.update_user_coins(target_id, bet)
            await database.db.update_user_coins(user_id, -bet)
            await interaction.followup.send(f"{user.mention} wins Connect 4!")
        elif view.winner == 2:
            await database.db.update_user_coins(user_id, bet)
            await database.db.update_user_coins(target_id, -bet)
            await interaction.followup.send(f"{interaction.user.mention} wins Connect 4!")
        else:
            await interaction.followup.send("It's a tie!")
        
        self.in_game.remove(user_id)
        self.in_game.remove(target_id)
        
        shared.rob_lock.remove(user_id)
        shared.rob_lock.remove(target_id)


async def setup(bot):
    await bot.add_cog(Games(bot))