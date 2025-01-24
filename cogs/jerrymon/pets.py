import discord
from discord import app_commands
import database

from .core import JerryMonCore, jerrymon_group

from views import PaginationView
from utils import calculate_jerrymon_max_xp, get_jerrymon_move_category, JerrymonMoveCategory, get_jerrymon_status_condition, get_jerrymon_type


class JerryMonPets(JerryMonCore):
    @jerrymon_group.command(name="get_free", description="Get free jerrymon (you must not have any).")
    async def get_free(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await database.db.verify_user(str(interaction.user.id))

        if await database.db.get_jerrymon_inventory_count(str(interaction.user.id)) > 0:
            await interaction.followup.send("You already have a jerrymon.")
            return

        random_jerrymon = await database.db.get_random_jerrymon()
        await database.db.add_jerrymon_to_inventory(str(interaction.user.id), random_jerrymon["id"])
        await interaction.followup.send(f"Got {random_jerrymon['name']} for you.")

    @jerrymon_group.command(name="party", description="List jerrymon you currently have on you.")
    async def party(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymons = await database.db.get_jerrymon_party(str(interaction.user.id))
        if len(jerrymons) == 0:
            await interaction.followup.send("You don't have any jerrymons.")
            return

        data = []
        for jerrymon in jerrymons:
            required_xp = calculate_jerrymon_max_xp(jerrymon["level"])
            data.append(
                {
                    "name": f"ID: {jerrymon['id']}, Name: {jerrymon['nickname'] or jerrymon['jerrymons']['name']}",
                    "value": f"Level: {jerrymon['level']} xp: {jerrymon['xp']}/{required_xp}, HP: {jerrymon['hp']} / {jerrymon['max_hp']}"
                }
            )

        view = await PaginationView.create(
            data,
            "Jerrymons",
            f"Your current jerrymons.\nYou have {len(jerrymons)} jerrymons.",
            interaction,
        )
        await view.wait()

    @jerrymon_group.command(name="box", description="List jerrymon in storage.")
    async def box(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymons = await database.db.get_jerrymon_box(str(interaction.user.id))
        if len(jerrymons) == 0:
            await interaction.followup.send("You don't have any jerrymons.")
            return

        data = []
        for jerrymon in jerrymons:
            required_xp = calculate_jerrymon_max_xp(jerrymon["level"])
            data.append(
                {
                    "name": f"ID: {jerrymon['id']}, Name: {jerrymon['nickname'] or jerrymon['jerrymons']['name']}",
                    "value": f"Level: {jerrymon['level']} xp: {jerrymon['xp']}/{required_xp}, HP: {jerrymon['hp']} / {jerrymon['max_hp']}"
                }
            )

        view = await PaginationView.create(
            data,
            "Jerrymons",
            f"Your current jerrymons.\nYou have {len(jerrymons)} jerrymons.",
            interaction,
        )
        await view.wait()

    @jerrymon_group.command(name="nickname", description="Nickname your jerry.")
    @app_commands.describe(jerrymon_id="Id of jerrymon.", nickname="Nickname of jerry.")
    async def nickname(self, interaction: discord.Interaction, jerrymon_id: int, nickname: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        if len(nickname) > 20:
            await interaction.followup.send("Nickname must be less than 20 characters.")
            return

        if len(nickname) < 1:
            await interaction.followup.send("Nickname must be greater than 0 characters.")
            return

        await database.db.set_jerrymon_nickname(str(interaction.user.id), jerrymon_id, nickname)
        await interaction.followup.send(f"Nickname set to {nickname} for ID: {jerrymon_id}.")

    @jerrymon_group.command(name="abandon", description="Abandon your jerry.")
    @app_commands.describe(jerrymon_id="Id of jerrymon.")
    async def abandon(self, interaction: discord.Interaction, jerrymon_id: int):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        await database.db.remove_jerrymon_from_inventory(str(interaction.user.id), jerrymon_id)
        await interaction.followup.send(f"Abandoned {jerrymon_id}.")

    @jerrymon_group.command(name="info", description="Get information on a jerrymon.")
    @app_commands.describe(jerrymon_name="Name of jerrymon.")
    async def info(self, interaction: discord.Interaction, jerrymon_name: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon(jerrymon_name)
        if not jerrymon:
            await interaction.followup.send(f"{jerrymon_name} not found.")
            return

        jerrymon_evolution = await database.db.get_jerrymon_by_id(jerrymon["evolution_id"]) if jerrymon["evolution_id"] else None

        embed = discord.Embed(
            title=f"Name: {jerrymon['name']}",
            description=f"Base HP: {jerrymon['base_hp']}\n"
            f"Base attack: {jerrymon['base_attack']}\n"
            f"Base defense: {jerrymon['base_defense']}\n"
            f"Base speed: {jerrymon['base_speed']}" +
            (f"\nEvolves to {jerrymon_evolution['name']} at level {
             jerrymon['evolution_level']}." if jerrymon_evolution else ""),
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @jerrymon_group.commmand(name="mine", description="Get information on your jerrymon.")
    async def mine(self, interaction: discord.Interaction, jerrymon_id: int):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        jerrymon_evolution = await database.db.get_jerrymon_by_id(jerrymon["evolution_id"]) if jerrymon["evolution_id"] else None

        embed = discord.Embed(
            title=f"Name: {jerrymon['nickname']
                           or jerrymon['jerrymons']['name']}",
            description=f"HP: {jerrymon['hp']}/{jerrymon['max_hp']}\n"
            f"MP: {jerrymon['mp']}/{jerrymon['max_mp']}\n"
            f"Attack: {jerrymon['attack']}\n"
            f"Defense: {jerrymon['defense']}\n"
            f"Speed: {jerrymon['speed']}")

        moves = await database.db.get_jerrymon_known_moves(jerrymon["id"])
        embed.add_field(
            name="Moves",
            value=f"{'\n'.join([f"Name: {move['jerrymon_moves']['name']}]\n"
                                f"Description: {
                move['jerrymon_moves']['description']}\n"
                f"Type: {
                get_jerrymon_status_condition(move['jerrymon_moves']['type'])
                if move['jerrymon_moves']['category'] == JerrymonMoveCategory.Status.value
                else get_jerrymon_type(move['jerrymon_moves']['type'])
            }\n"
                f"Category: {
                get_jerrymon_move_category(move['jerrymon_moves']['category'])
            }\n"
                f"Power: {
                move['jerrymon_moves']['power']}\n"
                f"Accuracy: {
                move['jerrymon_moves']['accuracy']}\n"
                f"MP cost: {
                move['jerrymon_moves']['mp']}"
                for move in moves])}")

        if jerrymon_evolution:
            embed.add_field(
                name="Evolution",
                value=f"Name: {jerrymon_evolution['name']}\n"
                f"Level: {jerrymon['evolution_level']}\n"
                f"Base HP: {jerrymon_evolution['base_hp']}\n"
                f"Base MP: {jerrymon_evolution['base_mp']}\n"
                f"Base Attack: {jerrymon_evolution['base_attack']}\n"
                f"Base Defense: {jerrymon_evolution['base_defense']}\n"
                f"Base Speed: {jerrymon_evolution['base_speed']}"
            )

        await interaction.followup.send(embed=embed)

    @jerrymon_group.command(name="give", description="Give your jerrymon to another player.")
    @app_commands.describe(user="User you want to give jerrymon to.", jerrymon_id="Id of jerrymon.")
    async def give(self, interaction: discord.Integration, user: discord.User, jerrymon_id: int):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        await database.db.transfer_jerrymon_from_inventory(str(interaction.user.id), jerrymon_id, str(user.id))
        await interaction.followup.send(f"Gave {jerrymon_id} to {user.name}.")

    @jerrymon_group.command(name="add_party", description="Add jerrymon to party.")
    @app_commands.describe(jerrymon_id="Id of jerrymon.")
    async def add_party(self, interaction: discord.Interaction, jerrymon_id: int):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        if jerrymon["in_party"]:
            await interaction.followup.send("Jerrymon is already in your party.")
            return

        party_len = await database.db.get_jerrymon_party_len(str(interaction.user.id))
        if party_len >= 6:
            await interaction.followup.send("You have too many jerrymons in your party.")
            return

        await database.db.move_jerrymon_party(str(interaction.user.id), jerrymon_id, True)
        await interaction.followup.send(f"Set {jerrymon_id} to your party.")

    @jerrymon_group.command(name="remove_party", description="Remove jerrymon from party.")
    @app_commands.describe(jerrymon_id="Id of jerrymon.")
    async def remove_party(self, interaction: discord.Interaction, jerrymon_id: int):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        jerrymon = await database.db.get_jerrymon_inventory_by_id(str(interaction.user.id), jerrymon_id)
        if not jerrymon:
            await interaction.followup.send("You don't have that jerrymon.")
            return

        if not jerrymon["in_party"]:
            await interaction.followup.send("Jerrymon is not in your party.")
            return

        await database.db.move_jerrymon_party(str(interaction.user.id), jerrymon_id, False)
        await interaction.followup.send(f"Removed {jerrymon_id} from your party.")

    # todo: show move information
