import discord
from discord import app_commands
import database
from views import JerrymonBattleView
import time
import random

from .core import JerryMonCore

# 5 minutes
HEAL_COOLDOWN = 60 * 5
HUNT_COOLDOWN = 60 * 30


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

        if await database.db.get_alive_jerrymons_count(str(interaction.user.id)) == 0:
            await interaction.followup.send("All your jerrymons are currently worn out.")
            return

        if await database.db.get_alive_jerrymons_count(str(user.id)) == 0:
            await interaction.followup.send(f"{user.name} has no alive jerrymons.")
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

        if str(interaction.user.id) in self.last_hunt_time and time.time() - self.last_hunt_time[str(interaction.user.id)] < HUNT_COOLDOWN:
            await interaction.followup.send(f"You can't battle again for {HUNT_COOLDOWN - int(time.time() - self.last_hunt_time[str(interaction.user.id)])} seconds.")
            return

        if await database.db.get_jerrymon_party_count(str(interaction.user.id)) == 0:
            await interaction.followup.send("You don't have any jerrymons in your party.")
            return

        if await database.db.get_alive_jerrymons_count(str(interaction.user.id)) == 0:
            await interaction.followup.send("All your jerrymons are currently worn out.")
            return

        self.last_hunt_time[str(interaction.user.id)] = time.time()

        if random.random() > 0.75:
            await interaction.followup.send("You didn't find anything.")
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

    @JerryMonCore.jerrymon_group.command(name="heal", description="Heal your jerrymon.")
    async def heal(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        user_id = str(interaction.user.id)

        if await database.db.get_jerrymon_party_count(user_id) == 0:
            await interaction.followup.send("You don't have any jerrymons in your party.")
            return

        if user_id in self.last_heal_time and time.time() - self.last_heal_time[user_id] < HEAL_COOLDOWN:
            await interaction.followup.send(
                f"You can't heal again for {
                    HEAL_COOLDOWN - int(time.time() - self.last_heal_time[user_id])} seconds."
            )
            return

        await database.db.heal_jerrymons(user_id)
        await interaction.followup.send("Healed your jerrymons.")

        self.last_heal_time[user_id] = time.time()
