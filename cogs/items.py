import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta

import database
from utils import handle_item_use, EquipType, get_equip_type, IntOrAll
from views import PaginationView


class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="item", description="Display the item.")
    async def item(self, interaction: discord.Interaction, item_name: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))
        item = await database.db.get_item(item_name)

        if not item:
            await interaction.followup.send(f"Item {item_name} not found.")
            return

        item = item[0]
        embed = discord.Embed(
            title=item["name"],
            description=f"**Description:** {item['description']}\n**Rarity:** {item['rarity']}\n**Price:** {item['price']}"
            + (
                f"\n**Level Required:** {item['level_require']}"
                if item["level_require"] is not None
                else ""
            ),
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="inventory", description="Display the user's inventory.")
    @app_commands.describe(user="User you want to check on.")
    async def inventory(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer()
        user_id = str(interaction.user.id if user is None else user.id)
        inventory = await database.db.get_inventory(user_id)

        if not inventory:
            await interaction.followup.send(f"You have no items in your inventory.")
            return

        data = []

        for item in inventory:
            uses_left = (
                f" - Uses left: {item['uses_left']}" if item["uses_left"] else ""
            )
            data.append(
                {"name": item["name"], "value": f"Count: {item['count']}" + uses_left}
            )

        view = await PaginationView.create(
            data,
            "Inventory",
            f"{interaction.user.name if user is None else user.name}'s inventory:",
            interaction,
        )
        await view.wait()

    @app_commands.command(name="use", description="Use an item from the inventory.")
    @app_commands.describe(item_name="The name of the item to use.")
    async def use(
        self, interaction: discord.Interaction, item_name: str, amount: str = "1"
    ):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        inventory = await database.db.get_inventory(user_id)
        if not inventory:
            await interaction.followup.send(f"You have no items in your inventory.")
            return

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        if parsed_amount.value == "all":
            amount = await database.db.get_item_inventory_count(user_id, item_name)
            if not amount:
                await interaction.followup.send(f"You don't have any {item_name}.")
                return

            amount = amount[0]["count"]
        else:
            amount = parsed_amount.value

        item = await database.db.get_item_inventory_count(user_id, item_name)
        print(item)

        if not item:
            await interaction.followup.send(
                f"Item {item_name} not found in your inventory."
            )
            return

        if amount < 1:
            await interaction.followup.send("You must use at least one item.")
            return

        if item[0]["count"] < amount:
            await interaction.followup.send(f"You don't have {amount} {item_name}.")
            return

        item = await database.db.get_item_inventory_by_id(user_id, item[0]["item_id"])

        if not await handle_item_use(user_id, item[0], amount, interaction, self):
            return

        # finally item count
        await database.db.use_item_inventory(user_id, item[0]["item_id"], amount)

        await interaction.followup.send(
            f"You used {amount} {item_name}{"s" if amount > 1 else ""}."
        )

    @app_commands.command(name="equip", description="Equip an item from the inventory.")
    @app_commands.describe(item_name="The name of the item to equip.")
    async def equip(self, interaction: discord.Interaction, item_name: str):
        await interaction.response.defer()

        user_id = str(interaction.user.id)

        item = await database.db.get_item_inventory_count(user_id, item_name)
        if not item:
            await interaction.followup.send(
                f"Item {item_name} not found in your inventory."
            )
            return

        item = item[0]

        equipped = await database.db.get_equipped(user_id)

        if (
            equipped["gun_id"] == item["item_id"]
            or equipped["accessory_id"] == item["item_id"]
        ):
            await interaction.followup.send(f"Item {item_name} is already equipped.")
            return

        equip_type = await get_equip_type(item["item_id"])
        if not equip_type:
            await interaction.followup.send(f"Item {item_name} can't be equipped.")
            return

        if equip_type == EquipType.GUN.value:
            await database.db.equip_gun(user_id, item["item_id"])
        elif equip_type == EquipType.ACCESSORY.value:
            await database.db.equip_accessory(user_id, item["item_id"])
        else:
            await interaction.followup.send(f"Shouldnt be happening {equip_type}")
            return

        await interaction.followup.send(f"You equipped {item_name}.")

    @app_commands.command(
        name="unequip", description="Unequip an item from the inventory."
    )
    @app_commands.describe(equip_type="What to unequip.")
    async def unequip(self, interaction: discord.Interaction, equip_type: EquipType):
        user_id = str(interaction.user.id)

        equipped = await database.db.get_equipped(user_id)

        if equip_type == EquipType.GUN:
            if not equipped["gun_id"]:
                await interaction.followup.send(f"Gun is not equipped.")
                return
            await database.db.unequip_gun(user_id)
        elif equip_type == EquipType.ACCESSORY:
            if not equipped["accessory_id"]:
                await interaction.followup.send(f"Accessory is not equipped.")
                return
            await database.db.unequip_accessory(user_id)
        else:
            await interaction.followup.send(f"Shouldnt be happening {equip_type}")
            return

        await interaction.followup.send(f"You unequipped {equip_type.name}.")

    @app_commands.command(
        name="equipped", description="Display the user's equipped items."
    )
    async def equipped(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        await database.db.verify_user(user_id)
        equipped = await database.db.get_equipped(user_id)

        embed = discord.Embed(
            title="Equipped",
            description=f"{interaction.user.name}'s equipped items:",
        )
        item_gun = (
            await database.db.get_item_by_id(equipped["gun_id"])
            if equipped["gun_id"]
            else None
        )
        embed.add_field(
            name="Gun", value=item_gun["name"] if item_gun else "None", inline=False
        )
        item_accessory = (
            await database.db.get_item_by_id(equipped["accessory_id"])
            if equipped["accessory_id"]
            else None
        )
        embed.add_field(
            name="Accessory",
            value=item_accessory["name"] if item_accessory else "None",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buffs", description="Display the user's buffs")
    async def buffs(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        await database.db.verify_user(user_id)
        buffs = await database.db.get_buff(user_id)
        embed = discord.Embed(
            title="Buffs",
            description=f"{interaction.user.name}'s buffs:",
        )
        if not buffs:
            await interaction.followup.send(
                content="You have no buffs.", ephemeral=True
            )
            return

        buffs = buffs[0]

        time_created = datetime.fromisoformat(buffs["time_created"])
        if time_created + timedelta(hours=2) < datetime.now(timezone.utc):
            await database.db.delete_buff(user_id)
            await interaction.followup.send(
                content="Your buff has expired.", ephemeral=True
            )
            return

        embed.add_field(
            name="Buffs",
            value=f"Coins multiplier: {buffs['coins_multiplier']}\nXP multiplier: {buffs['xp_multiplier']}\nSlave multiplier: {buffs['slaves_multiplier']}",
            inline=False,
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="give", description="Give item to a user.")
    async def give(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        item_name: str,
        amount: str = "1",
    ):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        await database.db.verify_user(user_id)
        await database.db.verify_user(str(user.id))

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be a integer or all.")
            return

        if parsed_amount.value == "all":
            amount = await database.db.get_item_inventory_count(user_id, item_name)
            if not amount:
                await interaction.followup.send(f"You don't have any {item_name}.")
                return

            amount = amount[0]["count"]
        else:
            amount = parsed_amount.value
            count = await database.db.get_item_inventory_count(user_id, item_name)
            if not count or amount > count[0]["count"]:
                await interaction.followup.send(f"You don't have enough {item_name}.")
                return

        item = await database.db.get_item(item_name)
        if not item:
            await interaction.followup.send(f"{item_name} doesn't exist!")
            return

        item_id = item[0]["id"]
        print(item_id)

        await database.db.transfer_item_inventory(
            user_id, str(user.id), item_id, amount
        )

        embed = discord.Embed(
            title="Give",
            description=f"You gave {user.name} {amount} {item_name}.",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Items(bot))
