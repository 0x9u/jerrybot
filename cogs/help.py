import discord
from discord.ext import commands
from discord import app_commands
import yaml
import os

from views import PaginationView

def load_changelog(yaml_file: str) -> dict:
    try:
        base_dir = os.getcwd()
        file_path = os.path.join(base_dir, yaml_file)
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except (FileNotFoundError, FileExistsError) as e:
        print(f"Error loading changelog file {yaml_file} - {e}")
        return {}

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.changelog = load_changelog("changelog.yaml")

    @app_commands.command(name="help", description="Display help information for all commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        data = []
        
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_app_commands()
            if not commands_list:
                continue
            
            cog_details = []
            for command in commands_list:
                if isinstance(command, app_commands.Group):
                    subcommands = "\n".join(
                        f"  ↳ `/{command.name} {subcommand.name}` - {subcommand.description or 'No description'}"
                        for subcommand in command.commands
                    )
                    cog_details.append(f"`/{command.name}` - {command.description or 'No description'}\n{subcommands}")
                else:
                    cog_details.append(f"`/{command.name}` - {command.description or 'No description'}")
            
            if cog_details:
                data.append({
                    "name" : cog_name,
                    "value" : "\n".join(cog_details)
                })
        
        view = await PaginationView.create(data, "Help", "List of commands by category", interaction)
        await view.wait()
    
    @app_commands.command(name="changelog",  description="Display the bot's changelog.")
    async def changelog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if not self.changelog:
            await interaction.followup.send("No changelog available.")
            return
                
        data = []
        for version, details in self.changelog.items():
            description = ""
            if 'date' in details:
                description += f"**Date**: {details['date']}\n"
            if 'changes' in details:
                changes = "\n".join(f"• {change}" for change in details['changes'])
                description += f"**Changes**:\n{changes}\n"
            
            data.append({
                "name" : version,
                "value" : description
            })
        
        view = await PaginationView.create(data, "Changelog", "List of changes made to the bot", interaction)
        await view.wait()

async def setup(bot):
    await bot.add_cog(Help(bot))
