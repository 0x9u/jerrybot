<<<<<<< Updated upstream
import discord
from discord.ext import commands
from discord import app_commands
import database
from views import BlackJackView
import numpy as np
import asyncio
from shared import shared
from utils import IntOrAll
from utils import slot_gamble
import random
from typing import Literal

GAMBLING_LIMIT = 10_000_000

# todo: put checks in one function and use it for all commands


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snake_eyes", description="Play snake eyes.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def snake_eyes(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Snake Eyes",
            description=f"Roll the dice and see if you win.\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)
        if global_bank < bet:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        message = await interaction.followup.send(embed=embed)

        shared.rob_lock.add(str(interaction.user.id))

        # placeholder field
        embed.add_field(name="Rolling dice...",
                        value="Rolling dice...", inline=False)

        # play rolling animation
        for _ in range(3):
            # remove field prev
            embed.set_field_at(
                0,
                name="Rolling dice...",
                value=f"Rolling dice... {np.random.randint(1, 7)} {
                    np.random.randint(1, 7)}",
                inline=False,
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        dice1 = np.random.randint(1, 7)
        dice2 = np.random.randint(1, 7)
        embed.set_field_at(
            0,
            name="Rolling dice...",
            value=f"You rolled {dice1} and {dice2}",
            inline=False,
        )
        await message.edit(embed=embed)

        if dice1 == 2 and dice2 == 2:
            embed.add_field(
                name="Snake Eyes!", value="You win 2x", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(str(interaction.user.id), bet)
            await database.db.update_user_coins(bot_id, -bet)
        elif dice1 % 2 == 0 and dice2 % 2 == 0:
            embed.add_field(
                name="Even numbers!", value="You win 1.5x", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(
                str(interaction.user.id), round(bet * 0.5)
            )
            await database.db.update_user_coins(bot_id, -round(0.5 * bet))
        else:
            embed.add_field(
                name="You lose.", value="You lose all your coins haha.", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="blackjack", description="Play blackjack.")
    async def blackjack(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Blackjack",
            description=f"Play blackjack and see if you win.\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        # placeholder embed
        embed.add_field(name="Your Deck", value="Cards: ", inline=False)
        embed.add_field(name="Dealer Deck", value="Cards: ", inline=False)

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        message = await interaction.followup.send(embed=embed)

        shared.rob_lock.add(str(interaction.user.id))

        view = BlackJackView(interaction.user.id, message, embed)

        await message.edit(embed=embed, view=view)

        await view.deal_initial_cards()

        await view.wait()

        embed.set_field_at(
            0,
            name="Your Deck",
            value=f"Cards: {', '.join(view.card_display_user)}",
            inline=False,
        )
        embed.set_field_at(
            1,
            name="Dealer Deck",
            value=f"Cards: {', '.join(view.card_display_dealer)}",
            inline=False,
        )

        await message.edit(embed=embed)

        if view.won:
            if view.double_down:
                embed.add_field(
                    name="You won! (Double down)", value="You won 2x", inline=False
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), bet)
                await database.db.update_user_coins(bot_id, -bet)
            else:
                embed.add_field(
                    name="You won!", value="You won 1.5x", inline=False
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(
                    str(interaction.user.id), round(bet * 0.5)
                )
                await database.db.update_user_coins(bot_id, -round(bet * 0.5))
        else:
            if view.tie:
                embed.add_field(
                    name="You tied!", value="You got your money back!", inline=False
                )
                await message.edit(embed=embed)
                shared.rob_lock.remove(str(interaction.user.id))
                return

            embed.add_field(
                name="You lost or timed out!", value="You lost all your coins.", inline=False
            )
            await message.edit(embed=embed)

            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="slot_machine", description="Play the slot machine.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def slot_machine(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Slot Machine",
            description=f"Spin the slot machine and test your luck!\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet * 10:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        shared.rob_lock.add(str(interaction.user.id))

        # Deduct the initial bet
        await database.db.update_user_coins(str(interaction.user.id), -bet)
        await database.db.update_user_coins(bot_id, bet)

        # Simulate slot machine spin
        # Define the slot symbols
        slot_emojis = [
            "🍒",
            "🍋",
            "🍉",
            "🍇",
            "🔔",
            "⭐",
            "💎",
            "💦",
            "🍆",
            "🤡",
            "💋",
            "💣",
            "🍉",
            "😏",
            "🍗",
            "👨🏿‍🦱",
            "🍗",
            "🚔",
            "🏚️",
            "🍑",
        ]

        winnings = slot_gamble(bet)
        # Approximation for the slot visuals
        slot1 = random.choice(slot_emojis)
        slot2 = random.choice(slot_emojis)
        slot3 = random.choice(slot_emojis)

        embed.add_field(
            name="Slot Machine Result",
            value=f"🎰 | {slot1} | {slot2} | {slot3} | 🎰",
            inline=False,
        )

        message = await interaction.followup.send(embed=embed)

        for _ in range(3):
            await asyncio.sleep(1)
            slot1 = random.choice(slot_emojis)
            slot2 = random.choice(slot_emojis)
            slot3 = random.choice(slot_emojis)
            embed.set_field_at(
                0,
                name="Slot Machine Result",
                value=f"🎰 | {slot1} | {slot2} | {slot3} | 🎰",
                inline=False,
            )
            await message.edit(embed=embed)

        if winnings > 0:
            embed.add_field(
                name="Congratulations!",
                value=f"You won {winnings} coins! 🎉",
                inline=False,
            )
            await database.db.update_user_coins(str(interaction.user.id), winnings)
            await database.db.update_user_coins(bot_id, -winnings)
        else:
            embed.add_field(
                name="Better Luck Next Time!",
                value="You lost your bet. 😢",
                inline=False,
            )

        await message.edit(embed=embed)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="roulette", description="Play roulette.")
    @app_commands.describe(
        bet="Amount of coins to bet.",
        number="Number to bet on.",
        color="Color to bet on.",
    )
    async def roulette(self, interaction: discord.Interaction, bet: str, number: int = None, color: Literal["red", "black", "green"] = None):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet * (35 if color is None else 14 if color == "green" else 2):
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if (color is not None and number is not None) or (color is None and number is None):
            await interaction.followup.send("Please enter either a color or a number.")
            return

        if number is not None and (number < 0 or number > 36):
            await interaction.followup.send("Please enter a number between 0 and 36.")
            return

        shared.rob_lock.add(str(interaction.user.id))

        embed = discord.Embed(
            title="Roulette",
            description=f"Spin the roulette wheel and see if you win.\n"
            f"Money betted on: {bet}\n"
            + (f"Bet Number: {number}" if number is not None else f"Bet Color: {color}"),
        )
        embed.add_field(
            name="Rolling the Wheel...",
            value=f"0",
            inline=False,
        )

        message = await interaction.followup.send(embed=embed)

        colors = {
            0: "green",
            **dict.fromkeys(range(1, 37, 2), "red"),
            **dict.fromkeys(range(2, 37, 2), "black")
        }

        for _ in range(3):
            random_number = random.randint(0, 36)
            embed.set_field_at(
                0,
                name="Rolling the Wheel...",
                value=f"{random_number} ({colors[random_number]})",
                inline=False
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        if number is not None:
            if random_number == number:
                winnings = bet * 35
                embed.add_field(
                    name="Congratulations!",
                    value=f"You won {winnings} coins (35x)!🎉",
                    inline=False,
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), winnings)
                await database.db.update_user_coins(bot_id, -winnings)
            else:
                embed.add_field(
                    name="Better Luck Next Time!",
                    value="You lost your bet. 😢",
                    inline=False,
                )
                await message.edit(embed=embed)
        else:
            if colors[random_number] == color:
                multiplier = 14 if color == "green" else 2
                winnings = bet * (multiplier)
                embed.add_field(
                    name="Congratulations!",
                    value=f"You won {winnings} coins ({multiplier}x)! 🎉",
                    inline=False,
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), winnings)
                await database.db.update_user_coins(bot_id, -winnings)
            else:
                embed.add_field(
                    name="Better Luck Next Time!",
                    value="You lost your bet. 😢",
                    inline=False,
                )
                await message.edit(embed=embed)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="russian_roulette", description="Play russian roulette.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def russian_roulette(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Bet must be an integer.")
            return

        bet = parsed_amount.value if parsed_amount.value != "all" else await database.db.get_user_coins(str(interaction.user.id))

        if await database.db.get_user_coins(str(interaction.user.id)) < bet:
            await interaction.followup.send("You don't have enough coins to play Russian Roulette.")
            return
        
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        global_bank = await database.db.get_user_coins(str(self.bot.user.id))
        if global_bank < bet * 100:
            await interaction.followup.send("The house doesn't have enough coins to make that bet.")
            return

        await database.db.update_user_coins(str(interaction.user.id), -bet)

        # show warning
        await interaction.followup.send(
            "WARNING: You will lose all your money on hand and some of your tycoon if you lose.\nAre you sure you want to play Russian Roulette (You can win up to 100x) (y/n)?"
        )
        choice = await self.bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id and m.content.lower() in [
                "y", "n"] and m.channel.id == interaction.channel_id, timeout=30
        )

        print("passed")

        if choice.content.lower() == "n":
            await interaction.followup.send("You chose not to play Russian Roulette.")
            return
    
        max_barrel = 10
        winnings = bet
        initial_multiplier = 10

        embed = discord.Embed(
            title="Russian Roulette",
            description=f"Play Russian Roulette and see if you win.\n"
            f"Money betted on: {bet}\n"
            f"Initial multiplier: {initial_multiplier}",
        )

        embed.add_field(
            name="Rolling the revolver...",
            value=f"🔫",
            inline=False,
        )

        shared.rob_lock.add(str(interaction.user.id))

        message = await interaction.followup.send(embed=embed)

        while True:

            await asyncio.sleep(3)

            bullet = random.randint(0, max_barrel)
            rolled = random.randint(0, max_barrel)

            embed.set_field_at(
                0,
                name="Rolling the revolver...",
                value=f"{rolled} (where the bullet is: {bullet}) (max barrel: {max_barrel})",
                inline=False
            )

            await message.edit(embed=embed)

            if bullet == rolled:
                # get all coins of user
                user_coins = await database.db.get_user_coins(str(interaction.user.id))
                await database.db.update_user_coins(str(interaction.user.id), -user_coins)
                await database.db.update_user_coins(str(self.bot.user.id), user_coins)
                # get slaves of user
                slaves = await database.db.get_slaves(str(interaction.user.id))
                lose_slaves = random.randint(
                    0, slaves) if slaves > 0 else 0
                if lose_slaves > 0:
                    await database.db.update_slaves(str(interaction.user.id), -lose_slaves)
                    await database.db.update_slaves(str(self.bot.user.id), lose_slaves)
                farms = await database.db.get_farms(str(interaction.user.id))
                lose_farms = random.randint(
                    0, farms) if farms > 0 else 0
                if lose_farms > 0:
                    await database.db.update_farms(str(interaction.user.id), -lose_farms)
                    await database.db.update_farms(str(self.bot.user.id), lose_farms)
                mines = await database.db.get_mines(str(interaction.user.id))
                lose_mines = random.randint(
                    0, mines) if mines > 0 else 0
                if lose_mines > 0:
                    await database.db.update_mines(str(interaction.user.id), -lose_mines)
                    await database.db.update_mines(str(self.bot.user.id), lose_mines)

                embed.add_field(
                    name="You Died!",
                    value="You lost your bet and all your coins. 😢" +
                    (f"\nYou lost {lose_slaves} slaves." if lose_slaves > 0 else "") +
                    (f"\nYou lost {lose_farms} farms." if lose_farms > 0 else "") +
                    (f"\nYou lost {
                     lose_mines} mines." if lose_mines > 0 else ""),
                    inline=False,
                )
                await message.edit(embed=embed)

                break
            else:
                if len(embed.fields) >= 2:
                    embed.set_field_at(
                        1,
                        name="You Survived!",
                        value="You won your bet. 🎉",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="You Survived!",
                        value="You won your bet. 🎉",
                        inline=False,
                    )
                
                max_barrel -= 1
                await message.edit(embed=embed)
                if max_barrel == 1:
                    embed.add_field(
                        name="Thanks for playing!",
                        value="Have a nice day!\n"
                        f"You won {winnings} coins ({initial_multiplier}x).",
                        inline=False,
                    )
                    await message.edit(embed=embed)
                    await database.db.update_user_coins(str(self.bot.user.id), -winnings)
                    await database.db.update_user_coins(str(interaction.user.id), winnings)
                    break
                # prompt for another bet
                await interaction.followup.send("Would you like to continue? (y/n)")
                response = await self.bot.wait_for("message", check=lambda m: m.author.id == interaction.user.id and m.channel == interaction.channel and m.content.lower() in ["y", "n"], timeout=30)
                if response.content.lower() != "y":
                    embed.add_field(
                        name="Thanks for playing!",
                        value="Have a nice day!\n"
                        f"You won {winnings} coins ({initial_multiplier}x).",
                        inline=False,
                    )
                    await message.edit(embed=embed)
                    winnings *= initial_multiplier
                    await database.db.update_user_coins(str(self.bot.user.id), -winnings)
                    await database.db.update_user_coins(str(interaction.user.id), winnings)
                    break

                initial_multiplier += 10
                # change description
                embed.description = f"Play Russian Roulette and see if you win.\nMoney betted on: {bet}\nInitial multiplier: {initial_multiplier}"

        shared.rob_lock.remove(str(interaction.user.id))


async def setup(bot):
    await bot.add_cog(Gambling(bot))
=======
import discord
from discord.ext import commands
from discord import app_commands
import database
from views import BlackJackView
import numpy as np
import asyncio
from shared import shared
from utils import IntOrAll
from utils import slot_gamble
import random
from typing import Literal

GAMBLING_LIMIT = 10_000_000

# todo: put checks in one function and use it for all commands


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snake_eyes", description="Play snake eyes.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def snake_eyes(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Snake Eyes",
            description=f"Roll the dice and see if you win.\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)
        if global_bank < bet:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        message = await interaction.followup.send(embed=embed)

        shared.rob_lock.add(str(interaction.user.id))

        # placeholder field
        embed.add_field(name="Rolling dice...",
                        value="Rolling dice...", inline=False)

        # play rolling animation
        for _ in range(3):
            # remove field prev
            embed.set_field_at(
                0,
                name="Rolling dice...",
                value=f"Rolling dice... {np.random.randint(1, 7)} {
                    np.random.randint(1, 7)}",
                inline=False,
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        dice1 = np.random.randint(1, 7)
        dice2 = np.random.randint(1, 7)
        embed.set_field_at(
            0,
            name="Rolling dice...",
            value=f"You rolled {dice1} and {dice2}",
            inline=False,
        )
        await message.edit(embed=embed)

        if dice1 == 2 and dice2 == 2:
            embed.add_field(
                name="Snake Eyes!", value="You win 2x", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(str(interaction.user.id), bet)
            await database.db.update_user_coins(bot_id, -bet)
        elif dice1 % 2 == 0 and dice2 % 2 == 0:
            embed.add_field(
                name="Even numbers!", value="You win 1.5x", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(
                str(interaction.user.id), round(bet * 0.5)
            )
            await database.db.update_user_coins(bot_id, -round(0.5 * bet))
        else:
            embed.add_field(
                name="You lose.", value="You lose all your coins haha.", inline=False
            )
            await message.edit(embed=embed)
            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="blackjack", description="Play blackjack.")
    async def blackjack(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Blackjack",
            description=f"Play blackjack and see if you win.\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        # placeholder embed
        embed.add_field(name="Your Deck", value="Cards: ", inline=False)
        embed.add_field(name="Dealer Deck", value="Cards: ", inline=False)

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        message = await interaction.followup.send(embed=embed)

        shared.rob_lock.add(str(interaction.user.id))

        view = BlackJackView(interaction.user.id, message, embed)

        await message.edit(embed=embed, view=view)

        await view.deal_initial_cards()

        await view.wait()

        embed.set_field_at(
            0,
            name="Your Deck",
            value=f"Cards: {', '.join(view.card_display_user)}",
            inline=False,
        )
        embed.set_field_at(
            1,
            name="Dealer Deck",
            value=f"Cards: {', '.join(view.card_display_dealer)}",
            inline=False,
        )

        await message.edit(embed=embed)

        if view.won:
            if view.double_down:
                embed.add_field(
                    name="You won! (Double down)", value="You won 2x", inline=False
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), bet)
                await database.db.update_user_coins(bot_id, -bet)
            else:
                embed.add_field(
                    name="You won!", value="You won 1.5x", inline=False
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(
                    str(interaction.user.id), round(bet * 0.5)
                )
                await database.db.update_user_coins(bot_id, -round(bet * 0.5))
        else:
            if view.tie:
                embed.add_field(
                    name="You tied!", value="You got your money back!", inline=False
                )
                await message.edit(embed=embed)
                shared.rob_lock.remove(str(interaction.user.id))
                return

            embed.add_field(
                name="You lost or timed out!", value="You lost all your coins.", inline=False
            )
            await message.edit(embed=embed)

            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="slot_machine", description="Play the slot machine.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def slot_machine(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        embed = discord.Embed(
            title="Slot Machine",
            description=f"Spin the slot machine and test your luck!\nMoney betted on: {
                bet}",
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet * 10:
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if str(interaction.user.id) in shared.rob_lock:
            await interaction.followup.send("You are already gambling.")
            return

        shared.rob_lock.add(str(interaction.user.id))

        # Deduct the initial bet
        await database.db.update_user_coins(str(interaction.user.id), -bet)
        await database.db.update_user_coins(bot_id, bet)

        # Simulate slot machine spin
        # Define the slot symbols
        slot_emojis = [
            "🍒",
            "🍋",
            "🍉",
            "🍇",
            "🔔",
            "⭐",
            "💎",
            "💦",
            "🍆",
            "🤡",
            "💋",
            "💣",
            "🍉",
            "😏",
            "🍗",
            "👨🏿‍🦱",
            "🍗",
            "🚔",
            "🏚️",
            "🍑",
        ]

        winnings = slot_gamble(bet)
        # Approximation for the slot visuals
        slot1 = random.choice(slot_emojis)
        slot2 = random.choice(slot_emojis)
        slot3 = random.choice(slot_emojis)

        embed.add_field(
            name="Slot Machine Result",
            value=f"🎰 | {slot1} | {slot2} | {slot3} | 🎰",
            inline=False,
        )

        message = await interaction.followup.send(embed=embed)

        for _ in range(3):
            await asyncio.sleep(1)
            slot1 = random.choice(slot_emojis)
            slot2 = random.choice(slot_emojis)
            slot3 = random.choice(slot_emojis)
            embed.set_field_at(
                0,
                name="Slot Machine Result",
                value=f"🎰 | {slot1} | {slot2} | {slot3} | 🎰",
                inline=False,
            )
            await message.edit(embed=embed)

        if winnings > 0:
            embed.add_field(
                name="Congratulations!",
                value=f"You won {winnings} coins! 🎉",
                inline=False,
            )
            await database.db.update_user_coins(str(interaction.user.id), winnings)
            await database.db.update_user_coins(bot_id, -winnings)
        else:
            embed.add_field(
                name="Better Luck Next Time!",
                value="You lost your bet. 😢",
                inline=False,
            )

        await message.edit(embed=embed)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="roulette", description="Play roulette.")
    @app_commands.describe(
        bet="Amount of coins to bet.",
        number="Number to bet on.",
        color="Color to bet on.",
    )
    async def roulette(self, interaction: discord.Interaction, bet: str, number: int = None, color: Literal["red", "black", "green"] = None):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Amount must be an integer or all.")
            return

        bet = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(str(interaction.user.id))
        )

        coins = await database.db.get_user_coins(str(interaction.user.id))
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        if coins < bet:
            await interaction.followup.send(
                "You don't have enough coins to make that bet."
            )
            return

        total_coins = await database.db.get_user_coins(
            str(interaction.user.id)
        ) + await database.db.get_bank_coins(str(interaction.user.id))
        if total_coins > GAMBLING_LIMIT:
            await interaction.followup.send(
                f"You have too many coins in your account. Please keep it under {
                    GAMBLING_LIMIT} coins."
            )
            return

        bot_id = str(self.bot.user.id)
        global_bank = await database.db.get_user_coins(bot_id)

        if global_bank < bet * (35 if color is None else 14 if color == "green" else 2):
            await interaction.followup.send(
                "The house doesn't have enough coins to make that bet."
            )
            return

        if (color is not None and number is not None) or (color is None and number is None):
            await interaction.followup.send("Please enter either a color or a number.")
            return

        if number is not None and (number < 0 or number > 36):
            await interaction.followup.send("Please enter a number between 0 and 36.")
            return

        shared.rob_lock.add(str(interaction.user.id))

        embed = discord.Embed(
            title="Roulette",
            description=f"Spin the roulette wheel and see if you win.\n"
            f"Money betted on: {bet}\n"
            + (f"Bet Number: {number}" if number is not None else f"Bet Color: {color}"),
        )
        embed.add_field(
            name="Rolling the Wheel...",
            value=f"0",
            inline=False,
        )

        message = await interaction.followup.send(embed=embed)

        colors = {
            0: "green",
            **dict.fromkeys(range(1, 37, 2), "red"),
            **dict.fromkeys(range(2, 37, 2), "black")
        }

        for _ in range(3):
            random_number = random.randint(0, 36)
            embed.set_field_at(
                0,
                name="Rolling the Wheel...",
                value=f"{random_number} ({colors[random_number]})",
                inline=False
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        if number is not None:
            if random_number == number:
                winnings = bet * 35
                embed.add_field(
                    name="Congratulations!",
                    value=f"You won {winnings} coins (35x)!🎉",
                    inline=False,
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), winnings)
                await database.db.update_user_coins(bot_id, -winnings)
            else:
                embed.add_field(
                    name="Better Luck Next Time!",
                    value="You lost your bet. 😢",
                    inline=False,
                )
                await message.edit(embed=embed)
        else:
            if colors[random_number] == color:
                multiplier = 14 if color == "green" else 2
                winnings = bet * (multiplier)
                embed.add_field(
                    name="Congratulations!",
                    value=f"You won {winnings} coins ({multiplier}x)! 🎉",
                    inline=False,
                )
                await message.edit(embed=embed)
                await database.db.update_user_coins(str(interaction.user.id), winnings)
                await database.db.update_user_coins(bot_id, -winnings)
            else:
                embed.add_field(
                    name="Better Luck Next Time!",
                    value="You lost your bet. 😢",
                    inline=False,
                )
                await message.edit(embed=embed)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="russian_roulette", description="Play russian roulette.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def russian_roulette(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

        await database.db.verify_user(str(interaction.user.id))

        try:
            parsed_amount = IntOrAll(bet)
        except ValueError:
            await interaction.followup.send("Bet must be an integer.")
            return

        bet = parsed_amount.value if parsed_amount.value != "all" else await database.db.get_user_coins(str(interaction.user.id))

        if await database.db.get_user_coins(str(interaction.user.id)) < bet:
            await interaction.followup.send("You don't have enough coins to play Russian Roulette.")
            return
        
        if bet <= 0:
            await interaction.followup.send("You can't bet 0 or less coins.")
            return

        global_bank = await database.db.get_user_coins(str(self.bot.user.id))
        if global_bank < bet * 100:
            await interaction.followup.send("The house doesn't have enough coins to make that bet.")
            return

        await database.db.update_user_coins(str(interaction.user.id), -bet)

        # show warning
        await interaction.followup.send(
            "WARNING: You will lose all your money on hand and some of your tycoon if you lose.\nAre you sure you want to play Russian Roulette (You can win up to 100x) (y/n)?"
        )
        choice = await self.bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id and m.content.lower() in [
                "y", "n"] and m.channel.id == interaction.channel_id, timeout=30
        )

        print("passed")

        if choice.content.lower() == "n":
            await interaction.followup.send("You chose not to play Russian Roulette.")
            return
    
        max_barrel = 10
        winnings = bet
        initial_multiplier = 10

        embed = discord.Embed(
            title="Russian Roulette",
            description=f"Play Russian Roulette and see if you win.\n"
            f"Money betted on: {bet}\n"
            f"Initial multiplier: {initial_multiplier}",
        )

        embed.add_field(
            name="Rolling the revolver...",
            value=f"🔫",
            inline=False,
        )

        shared.rob_lock.add(str(interaction.user.id))

        message = await interaction.followup.send(embed=embed)

        while True:

            await asyncio.sleep(3)

            bullet = random.randint(0, max_barrel)
            rolled = random.randint(0, max_barrel)

            embed.set_field_at(
                0,
                name="Rolling the revolver...",
                value=f"{rolled} (where the bullet is: {bullet}) (max barrel: {max_barrel})",
                inline=False
            )

            await message.edit(embed=embed)

            if bullet == rolled:
                # get all coins of user
                user_coins = await database.db.get_user_coins(str(interaction.user.id))
                await database.db.update_user_coins(str(interaction.user.id), -user_coins)
                await database.db.update_user_coins(str(self.bot.user.id), user_coins)
                # get slaves of user
                slaves = await database.db.get_slaves(str(interaction.user.id))
                lose_slaves = random.randint(
                    0, slaves) if slaves > 0 else 0
                if lose_slaves > 0:
                    await database.db.update_slaves(str(interaction.user.id), -lose_slaves)
                    await database.db.update_slaves(str(self.bot.user.id), lose_slaves)
                farms = await database.db.get_farms(str(interaction.user.id))
                lose_farms = random.randint(
                    0, farms) if farms > 0 else 0
                if lose_farms > 0:
                    await database.db.update_farms(str(interaction.user.id), -lose_farms)
                    await database.db.update_farms(str(self.bot.user.id), lose_farms)
                mines = await database.db.get_mines(str(interaction.user.id))
                lose_mines = random.randint(
                    0, mines) if mines > 0 else 0
                if lose_mines > 0:
                    await database.db.update_mines(str(interaction.user.id), -lose_mines)
                    await database.db.update_mines(str(self.bot.user.id), lose_mines)

                embed.add_field(
                    name="You Died!",
                    value="You lost your bet and all your coins. 😢" +
                    (f"\nYou lost {lose_slaves} slaves." if lose_slaves > 0 else "") +
                    (f"\nYou lost {lose_farms} farms." if lose_farms > 0 else "") +
                    (f"\nYou lost {
                     lose_mines} mines." if lose_mines > 0 else ""),
                    inline=False,
                )
                await message.edit(embed=embed)

                break
            else:
                if len(embed.fields) >= 2:
                    embed.set_field_at(
                        1,
                        name="You Survived!",
                        value="You won your bet. 🎉",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="You Survived!",
                        value="You won your bet. 🎉",
                        inline=False,
                    )
                
                winnings *= initial_multiplier
                max_barrel -= 1
                await message.edit(embed=embed)
                if max_barrel == 1:
                    embed.add_field(
                        name="Thanks for playing!",
                        value="Have a nice day!\n"
                        f"You won {winnings} coins ({initial_multiplier}x).",
                        inline=False,
                    )
                    await message.edit(embed=embed)
                    await database.db.update_user_coins(str(self.bot.user.id), -winnings)
                    await database.db.update_user_coins(str(interaction.user.id), winnings)
                    break
                # prompt for another bet
                await interaction.followup.send("Would you like to continue? (y/n)")
                response = await self.bot.wait_for("message", check=lambda m: m.author.id == interaction.user.id and m.channel == interaction.channel and m.content.lower() in ["y", "n"], timeout=30)
                if response.content.lower() != "y":
                    embed.add_field(
                        name="Thanks for playing!",
                        value="Have a nice day!\n"
                        f"You won {winnings} coins ({initial_multiplier}x).",
                        inline=False,
                    )
                    await message.edit(embed=embed)
                    await database.db.update_user_coins(str(self.bot.user.id), -winnings)
                    await database.db.update_user_coins(str(interaction.user.id), winnings)
                    break

                initial_multiplier += 10
                # change description
                embed.description = f"Play Russian Roulette and see if you win.\nMoney betted on: {bet}\nInitial multiplier: {initial_multiplier}"

        shared.rob_lock.remove(str(interaction.user.id))


async def setup(bot):
    await bot.add_cog(Gambling(bot))
>>>>>>> Stashed changes
