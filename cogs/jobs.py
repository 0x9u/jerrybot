import discord
from discord import app_commands
from discord.ext import commands
from views import PaginationView
from utils import job_lootbox

import database
from datetime import datetime, timezone, timedelta
import random


class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    job_group = app_commands.Group(name="jobs", description="Get ur jobs!!")

    @job_group.command(
        name="list",
        description="List all available jobs",
    )
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        jobs = await database.db.get_jobs_list()
        data = []
        for job in jobs:
            data.append(
                {
                    "name": job["name"],
                    "value": f"{job['description']} - ${job['rate']}/30 minutes{' - Level required: ' + str(job['level_require']) if job['level_require'] is not None else ''}",
                }
            )

        view = await PaginationView.create(data, "Jobs", "Get a job here!", interaction)
        await view.wait()

    @app_commands.command(
        name="work",
        description="Work at your job",
    )
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)

        await database.db.verify_user(user_id)

        job_id = await database.db.get_current_job(user_id)
        if not job_id:
            await interaction.followup.send("You don't have a job yet.")
            return

        job = await database.db.get_job_by_id(job_id)

        if job is None:
            await interaction.followup.send("Job not found.")
            return

        job = job[0]

        bot_id = str(self.bot.user.id)
        bot_coins = await database.db.get_user_coins(bot_id)
        if bot_coins < job["rate"]:
            await interaction.followup.send(
                "Your boss doesn't have enough money to pay you."
            )
            return

        last_worked_timestamp = await database.db.get_last_worked(user_id)
        last_worked = (
            datetime.fromisoformat(last_worked_timestamp)
            if last_worked_timestamp is not None
            else None
        )
        time_elapsed = (
            datetime.now(timezone.utc) - last_worked
            if last_worked is not None
            else timedelta(minutes=30)
        )
        if time_elapsed < timedelta(minutes=30):
            minutes = int((timedelta(minutes=30) - time_elapsed).total_seconds() // 60)
            seconds = int((timedelta(minutes=30) - time_elapsed).total_seconds() % 60)
            await interaction.followup.send(
                f"Please wait {minutes} minutes and {seconds} seconds before working again."
            )
            return

        await database.db.update_last_worked(user_id, datetime.now(timezone.utc))

        got_item = random.random() > 0.5
        item_name = None

        if got_item:
            item_id = await job_lootbox(job["id"])
            await database.db.add_item_to_inventory(user_id, item_id, 1)
            item_name = (await database.db.get_item_by_id(item_id))["name"]

        await database.db.update_user_coins(user_id, job["rate"])
        await database.db.update_user_coins(bot_id, -job["rate"])

        await interaction.followup.send(
            f"You worked as {job['name']} and earned ${job['rate']}."
            + (f"\nAlso your boss gave you a {item_name} for your outstanding work!"
            if got_item
            else "")
        )

    @job_group.command(
        name="get",
        description="Get a job",
    )
    async def get(self, interaction: discord.Interaction, job_name: str):
        await interaction.response.defer()

        job = await database.db.get_job(job_name)
        if not job:
            await interaction.followup.send("Job not found.")
            return

        job = job[0]

        if job["level_require"] is not None and job[
            "level_require"
        ] > await database.db.get_user_level(str(interaction.user.id)):
            await interaction.followup.send(
                f"You need to be level {job['level_require']} to get this job."
            )
            return

        await database.db.set_current_job(str(interaction.user.id), job["id"])

        await interaction.followup.send(f"You are now working as {job['name']}!")

    @job_group.command(
        name="quit",
        description="Quit your job",
    )
    async def quit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        job_id = await database.db.get_current_job(str(interaction.user.id))
        if job_id is None:
            await interaction.followup.send("You don't have a job to quit.")
            return

        await database.db.set_current_job(str(interaction.user.id), None)
        await interaction.followup.send("You have quit your job.")

    @job_group.command(
        name="current",
        description="Get your current job",
    )
    async def current(self, interaction: discord.Interaction):
        await interaction.response.defer()

        job_id = await database.db.get_current_job(str(interaction.user.id))
        if job_id is None:
            await interaction.followup.send("You don't have a job.")
            return

        job = await database.db.get_job_by_id(job_id)
        if job is None:
            await interaction.followup.send("Job not found.")
            return

        job = job[0]

        await interaction.followup.send(f"You are working as {job['name']}!")


async def setup(bot):
    await bot.add_cog(Jobs(bot))
