import discord
from discord import app_commands
from discord.ext import commands
import database

from utils import adjust_price, IntOrAll, ALIAS
from views import PaginationView


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    shop_group = app_commands.Group(name="shop", description="Buy stuff here!!")

    @shop_group.command(name="list", description="Display the shop.")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = []
        for item in await database.db.get_items_shop():
            level_require_string = (
                f"\nRequires level {item['level_require']}"
                if item["level_require"] and item["level_require"] > 0
                else ""
            )
            current_demand = await database.db.get_current_demand(item["id"])
            baseline_demand = await database.db.get_baseline_demand(item["id"])
            price = adjust_price(item["price"], current_demand, baseline_demand)

            data.append(
                {
                    "name": f"{item["name"]} - ${price}",
                    "value": f"Description: {item['description']}{ level_require_string }",
                }
            )

        view = await PaginationView.create(
            data, "Shop", "Get ya stuff here!", interaction
        )

        await view.wait()

    @shop_group.command(name="buy", description="Buy an item from the shop.")
    @app_commands.describe(item_name="The name of the item to buy.")
    async def buy(
        self, interaction: discord.Interaction, item_name: str, amount: str = "1"
    ):
        await interaction.response.defer()

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer.")
            return

        item_name = item_name if ALIAS.get(item_name) is None else ALIAS[item_name]

        item = await database.db.get_item_shop(item_name)
        if not item:
            await interaction.followup.send(f"Item {item_name} not found in the shop.")
            return

        item = item[0]

        current_demand = await database.db.get_current_demand(item["id"])
        baseline_demand = await database.db.get_baseline_demand(item["id"])

        amount = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
            // adjust_price(item["price"], current_demand, baseline_demand)
        )

        price = adjust_price(item["price"], current_demand, baseline_demand) * amount

        if amount < 1:
            await interaction.followup.send("You must buy at least one item.")
            return

        # alias

        user_id = str(interaction.user.id)
        user_coins = await database.db.get_user_coins(user_id)

        if user_coins < price:
            await interaction.followup.send(
                f"You don't have enough coins to buy {item_name}."
            )
            return

        level = await database.db.get_user_level(user_id)
        if item["level_require"] is not None and level < item["level_require"]:
            await interaction.followup.send(
                f"You need to be level {item['level_require']} to buy {item_name}."
            )
            return

        await database.db.add_item_to_inventory(user_id, item["id"], amount)

        await database.db.update_user_coins(user_id, -price)
        # get bots id
        bot_id = str(self.bot.user.id)
        await database.db.update_user_coins(bot_id, price)

        await database.db.update_item_demand(item["id"], amount)

        await interaction.followup.send(
            f"You bought {amount} {item_name}{"s" if amount > 1 else ""}."
        )

    @shop_group.command(name="sell", description="Sell an item from the inventory.")
    @app_commands.describe(item_name="The name of the item to sell.")
    async def sell(
        self, interaction: discord.Interaction, item_name: str, amount: str = "1"
    ):
        await interaction.response.defer()

        item = await database.db.get_item_inventory_count(
            str(interaction.user.id), item_name
        )
        if not item:
            await interaction.followup.send(
                f"Item {item_name} not found in your inventory."
            )
            return

        item = item[0]

        shop_item = await database.db.get_item(item_name)

        if not shop_item:
            await interaction.followup.send(f"Item {item_name} not sellable.")
            return

        shop_item = shop_item[0]

        print(item)
        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        if parsed_amount.value == "all":
            amount = item["count"]
        else:
            amount = parsed_amount.value
            if amount > item["count"]:
                await interaction.followup.send(f"You don't have enough {item_name}.")
                return

        current_demand = await database.db.get_current_demand(item["item_id"])
        baseline_demand = await database.db.get_baseline_demand(item["item_id"])
        price = (
            round(
                adjust_price(shop_item["price"], current_demand, baseline_demand) * 0.75
                if shop_item["in_shop"]
                else shop_item["price"]
            )
            * amount
        )

        bot_id = str(self.bot.user.id)
        bot_coins = await database.db.get_user_coins(bot_id)
        if bot_coins < price:
            await interaction.followup.send(
                f"I don't have enough coins to buy your {item_name}."
            )
            return

        # 75% of the sell price
        await database.db.update_user_coins(str(interaction.user.id), price)
        await database.db.update_user_coins(bot_id, -price)

        await database.db.remove_item_from_inventory(
            str(interaction.user.id), item["item_id"], amount
        )

        await interaction.followup.send(
            f"You sold {amount} {item_name}{"s" if amount > 1 else ""} for {price} coins."
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
