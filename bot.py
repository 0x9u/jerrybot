import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

import logging

logging.getLogger("discord").setLevel(logging.ERROR)
logging.getLogger("discord.http").setLevel(logging.INFO)

import database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

activity = discord.Activity(
    type=discord.ActivityType.watching, name="the economy go down the drain"
)

bot = commands.Bot(command_prefix="!", activity=activity, intents=intents)

@bot.event
async def on_ready():
    print("Ready!")
    try:
        # make sure bot itself is in db
        await database.db.verify_user(str(bot.user.id))
        await bot.tree.sync()
    except Exception as e:
        print(e)
        await bot.close()


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CommandInvokeError):
        await interaction.response.send_message(
            f"Command error: {error.original}", ephemeral=True
        )
        print(f"Error: {error.original}")
    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Command not found.", ephemeral=True)
    else:
        await interaction.followup.send(
            f"An unknown error occurred. {error}", ephemeral=True
        )
        print(f"Unknown error: {error}")


async def main():
    await database.initialise_db()
    print(f"db: {database.db}")
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
