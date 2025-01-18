import discord
from discord import app_commands
from discord.ext import commands
import database
import asyncio

from utils import IntOrAll
from views import PaginationView


class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    market_group = app_commands.Group(name="market", description="Market commands.")

    @market_group.command(name="list", description="Display the market.")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        market_data = await database.db.get_market()
        if not market_data:
            embed = discord.Embed(
                title="Market",
                description="Get ya stuff here!",
            )
            embed.add_field(name="No items in the market.", value="Come back later.")
            await interaction.followup.send(embed=embed)
            return
        user_ids = [user["user_id"] for user in market_data]
        users_data = await asyncio.gather(
            *(self.bot.fetch_user(user_id) for user_id in user_ids)
        )

        data = []

        for item, users_data in zip(market_data, users_data):
            seller_name = users_data.name
            data.append(
                {
                    "name": f"{item['name']} - Amount {item['amount']} - ${item['sell_price']}",
                    "value": f"Seller: {seller_name}\n Buy Market ID: {item['id']}",
                }
            )

        view = await PaginationView.create(
            data,
            "Market",
            "Get ya stuff here!",
            interaction,
        )

        await view.wait()

    @market_group.command(name="buy", description="Buy an item from the market.")
    @app_commands.describe(buy_market_id="The ID of the item to buy.")
    async def buy(self, interaction: discord.Interaction, buy_market_id: int):
        await interaction.response.defer()

        item = await database.db.get_item_market(buy_market_id)

        embed = discord.Embed(
            title="Market",
        )

        if not item:
            embed.description = f"Market ID {buy_market_id} not found in the market."
            await interaction.followup.send(embed=embed)
            return

        item = item[0]

        user_id = str(interaction.user.id)
        user_coins = await database.db.get_user_coins(user_id)

        if user_id == item["user_id"]:
            embed.description = f"You can't buy your own item."
            await interaction.followup.send(embed=embed)
            return

        price = item["sell_price"]
        name = item["items"]["name"]

        if user_coins < price:
            embed.description = f"You don't have enough coins to buy {name}."
            await interaction.followup.send(embed=embed)
            return

        await database.db.update_user_coins(user_id, -price)
        await database.db.update_user_coins(item["user_id"], price)

        await database.db.buy_market_item(user_id, buy_market_id)

        seller_name = await self.bot.fetch_user(item["user_id"])

        await interaction.followup.send(
            f"Bought {name} for {price} coins from {seller_name}."
        )

    @market_group.command(name="sell", description="Sell an item to the market.")
    @app_commands.describe(
        item_name="The name of the item to sell.",
        sell_price="The price to sell the item for.",
    )
    async def sell(
        self, interaction: discord.Interaction, item_name: str, sell_price: int, amount: str = "1"
    ):
        await interaction.response.defer()

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer.")
            return
        
        if parsed_amount.value == "all":
            amount = len(await database.db.get_item_inventory_by_id(user_id, item["item_id"]))
            if not amount:
                await interaction.followup.send(f"You don't have any {item_name} or all of {item_name} is already in the market.")
                return

            amount = amount[0]["count"]
        else:
            amount = parsed_amount.value

        user_id = str(interaction.user.id)

        item = await database.db.get_item_inventory_by_name(user_id, item_name)

        if not item:
            await interaction.followup.send(
                f"You don't have {item_name} in your inventory."
            )
            return

        item = item[0]

        if amount > len(await database.db.get_item_inventory_by_id(user_id, item["item_id"])):
            await interaction.followup.send(
                f"You dont have enough of {item_name} to sell."
            )
            return

        embed = discord.Embed(
            title="Market",
        )

        market_id = await database.db.sell_item_market(user_id, item["item_id"], sell_price, amount)

        embed.add_field(
            name=f"Your {item_name} has been added to the market.",
            value=f"Market ID: {market_id}",
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    @market_group.command(name="remove", description="Remove an item from the market.")
    @app_commands.describe(market_item_id="The ID of the item to remove.")
    async def remove(
        self, interaction: discord.Interaction, market_item_id: int
    ):
        await interaction.response.defer()

        market_item = await database.db.get_item_market(market_item_id)
        if not market_item:
            await interaction.followup.send(
                f"Market ID {market_item_id} not found in the market."
            )
            return

        if market_item[0]["user_id"] != str(interaction.user.id):
            await interaction.followup.send(
                "You can only remove your own items from the market."
            )
            return

        await database.db.delete_item_market(market_item_id)

        await interaction.followup.send(
            f"Market ID {market_item_id} has been removed from the market."
        )

    @market_group.command(
        name="my_items", description="Display the items you have in the market."
    )
    async def my_items(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = await database.db.get_market_by_user_id(str(interaction.user.id))

        embed = discord.Embed(
            title="Market",
        )

        if not data:
            embed.description = "You have no items in the market."
            await interaction.followup.send(embed=embed)
            return

        for item in data:
            print(item)
            embed.add_field(
                name=f"{item['name']} - {item['amount']} - {item['sell_price']} coins",
                value=f"Buy Market ID: {item['id']}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Market(bot))
