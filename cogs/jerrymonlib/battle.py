import discord
from discord import app_commands
import database
from views import JerrymonBattleView

from .core import JerryMonCore

class JerryMonBattle(JerryMonCore):
    @JerryMonCore.jerrymon_group.command(name="battle", description="Battle other jerrymon")
    @app_commands.describe(user="User you wanna battle with.")
    async def battle(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        await database.db.verify_user(str(user.id))
        
        if await database.db.get_jerrymon_party_count(str(interaction.user.id)) == 0:
            await interaction.followup.send("You don't have any jerrymons in your party.")
            return
        
        if await database.db.get_jerrymon_party_count(str(user.id)) == 0:
            await interaction.followup.send(f"{user.name} doesn't have any jerrymons in their party.")
            return

        view = await JerrymonBattleView.create(
            "Jerrymon Battle",
            f"You are battling against {user.name}",
            interaction,
            interaction.user,
            user
        )
        
        await view.wait()

    @JerryMonCore.jerrymon_group.command(name="hunt", description="Hunt for jerrymon.")
    async def hunt(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await database.db.verify_user(str(interaction.user.id))
                
        if await database.db.get_jerrymon_party_count(str(interaction.user.id)) == 0:
            await interaction.followup.send("You don't have any jerrymons in your party.")
            return
        
        random_jerrymon = await database.db.get_random_jerrymon()
        
        # horrible code ;(
        jerrymon = await database.db.get_jerrymon_by_id(random_jerrymon)
        
        view = await JerrymonBattleView.create(
            "Jerrymon Hunt",
            f"You found a {jerrymon['name']}!",
            interaction,
            interaction.user,
            jerrymon_id=random_jerrymon
        )
        
        await view.wait()
        
