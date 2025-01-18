import discord
from discord.ext import commands
from discord import app_commands
import yfinance as yf
import database
from utils import get_top_stocks, IntOrAll
from views import PaginationView


class Investing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    investing_group = app_commands.Group(
        name="investing", description="INVEST NOW INVEST NOW"
    )

    @investing_group.command(
        name="portfolio", description="Check your stock portfolio."
    )
    async def portfolio(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer()
        user_id = str(interaction.user.id if user is None else user.id)
        await database.db.verify_user(user_id)
        portfolio = await database.db.get_user_portfolio(user_id)  # Assumes a portfolio schema
        total_value = 0

        data = []

        for row in portfolio:
            symbol = row["symbol"]
            shares = row["shares"]

            # Fetch real-time stock data using yfinance
            stock = yf.Ticker(symbol)
            try:
                price = stock.history(period="1d")["Close"].iloc[-1]
                prev_close = stock.history(period="5d")["Close"].iloc[-2]
                daily_change = ((price - prev_close) / prev_close) * 100
            except Exception as e:
                await interaction.followup.send(
                    f"Error fetching stock data for {symbol}: {str(e)}"
                )
                continue

            holding_value = shares * price
            total_value += holding_value
            data.append(
                {
                    "name": f"{symbol}",
                    "value": (
                        f"Shares: {shares}\n"
                        f"Price: ${price:.2f}\n"
                        f"Value: ${holding_value:.2f}\n"
                        f"Daily Change: {daily_change:.2f}%"
                    ),
                }
            )

        view = await PaginationView.create(
            data,
            f"{(interaction.user if user is None else user).name}'s Portfolio",
            f"Total Portfolio Value: ${total_value:.2f}\nYour current stock holdings and values:",
            interaction,
        )

        await view.wait()

    @investing_group.command(name="stocks", description="See top 10 stocks.")
    async def stocks(self, interaction: discord.Interaction):
        await interaction.response.defer()

        top_stocks = get_top_stocks()

        embed = discord.Embed(
            title="Top 10 Stocks",
            description="Here are the top 10 stocks in the market:",
        )

        for i, stock in enumerate(top_stocks, start=1):
            embed.add_field(
                name=f"{i}. {stock['Ticker']}",
                value=f"Start Price: ${stock['Start Price']:.2f} - End Price: ${stock['End Price']:.2f} - Change: {stock['Change']:.2f}%",
                inline=False,
            )
        await interaction.followup.send(embed=embed)

    @investing_group.command(name="buy", description="Buy shares of a stock.")
    @app_commands.describe(
        symbol="Stock ticker symbol", shares="Number of shares to buy."
    )
    async def buy(self, interaction: discord.Interaction, symbol: str, shares: str):
        await interaction.response.defer()

        try:
            parsed_shares = IntOrAll(shares)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return
        
        stock = yf.Ticker(symbol)
        try:
            price = stock.history(period="1d")["Close"].iloc[-1]
        except IndexError:
            await interaction.followup.send("Invalid stock ticker symbol.")
            return
        
        await database.db.verify_user(str(interaction.user.id))
        coins = await database.db.get_user_coins(str(interaction.user.id))

        shares = (
            parsed_shares.value
            if parsed_shares.value != "all"
            else int(coins // price)
        )

        if shares <= 0:
            await interaction.followup.send("You must buy at least 1 share.")
            return
        symbol = symbol.upper()

        cost = round(shares * price)
        if coins < cost:
            await interaction.followup.send(
                f"You don't have enough coins. Cost: ${cost:.2f}"
            )
            return

        await database.db.update_user_coins(str(interaction.user.id), -cost)
        await database.db.update_user_portfolio(str(interaction.user.id), symbol, shares)
        await interaction.followup.send(
            f"You bought {shares} shares of {symbol} for ${cost:.2f}!"
        )

    @investing_group.command(name="sell", description="Sell shares of a stock.")
    @app_commands.describe(
        symbol="Stock ticker symbol", shares="Number of shares to sell."
    )
    async def sell_stock(
        self, interaction: discord.Interaction, symbol: str, shares: int
    ):
        await interaction.response.defer()
        if shares <= 0:
            await interaction.followup.send("You must sell at least 1 share.")
            return

        await database.db.verify_user(str(interaction.user.id))
        portfolio = await database.db.get_user_portfolio_stock(str(interaction.user.id), symbol)

        if not portfolio:
            await interaction.followup.send(
                f"You don't own any shares of {symbol} or it doesn't exist."
            )
            return

        stock = yf.Ticker(symbol)
        try:
            price = stock.history(period="1d")["Close"].iloc[-1]
        except IndexError:
            await interaction.followup.send("Invalid stock ticker symbol.")
            return

        earnings = round(shares * price)
        taxed = int(earnings * 0.1)
        earnings -= taxed

        bot_id = str(self.bot.user.id)
        await database.db.update_user_coins(str(interaction.user.id), earnings)
        await database.db.update_user_portfolio(str(interaction.user.id), symbol, -shares)
        await database.db.update_user_coins(bot_id, taxed)
        await interaction.followup.send(
            f"You sold {shares} shares of {symbol} for ${earnings}!\nYou were taxed ${taxed}."
        )


async def setup(bot):
    await bot.add_cog(Investing(bot))
