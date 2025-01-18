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

GAMBLING_LIMIT = 10_000_000


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snake_eyes", description="Play snake eyes.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def snake_eyes(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

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
            description=f"Roll the dice and see if you win.\nMoney betted on: {bet}",
        )

        await database.db.verify_user(str(interaction.user.id))
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
                f"You have too many coins in your account. Please keep it under {GAMBLING_LIMIT} coins."
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
        embed.add_field(name="Rolling dice...", value="Rolling dice...", inline=False)

        # play rolling animation
        for _ in range(3):
            # remove field prev
            embed.set_field_at(
                0,
                name="Rolling dice...",
                value=f"Rolling dice... {np.random.randint(1, 7)} {np.random.randint(1, 7)}",
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
            await interaction.followup.send("Snake Eyes! You win 2x")
            await database.db.update_user_coins(str(interaction.user.id), bet)
            await database.db.update_user_coins(bot_id, -bet)
        elif dice1 % 2 == 0 and dice2 % 2 == 0:
            await interaction.followup.send("Even numbers! You win 1.5x")
            await database.db.update_user_coins(
                str(interaction.user.id), round(bet * 0.5)
            )
            await database.db.update_user_coins(bot_id, -round(0.5 * bet))
        else:
            await interaction.followup.send("You lost all your coins haha.")
            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="blackjack", description="Play blackjack.")
    async def blackjack(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

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
            description=f"Play blackjack and see if you win.\nMoney betted on: {bet}",
        )

        await database.db.verify_user(str(interaction.user.id))
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
                f"You have too many coins in your account. Please keep it under {GAMBLING_LIMIT} coins."
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
                await interaction.followup.send(
                    f"You won! {interaction.user.mention} You doubled your bet."
                )
                await database.db.update_user_coins(str(interaction.user.id), bet)
                await database.db.update_user_coins(bot_id, -bet)
            else:
                await interaction.followup.send(
                    f"You won! {interaction.user.mention} You won 1.5x"
                )
                await database.db.update_user_coins(
                    str(interaction.user.id), round(bet * 0.5)
                )
                await database.db.update_user_coins(bot_id, -round(bet * 0.5))
        else:
            if view.tie:
                await interaction.followup.send(
                    f"You tied (You don't lose anything). {interaction.user.mention}"
                )
                shared.rob_lock.remove(str(interaction.user.id))
                return

            await interaction.followup.send(
                f"You lost or the game timed out. {interaction.user.mention}"
            )
            await database.db.update_user_coins(str(interaction.user.id), -bet)
            await database.db.update_user_coins(bot_id, bet)

        shared.rob_lock.remove(str(interaction.user.id))

    @app_commands.command(name="slot_machine", description="Play the slot machine.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def slot_machine(self, interaction: discord.Interaction, bet: str):
        await interaction.response.defer()

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
            description=f"Spin the slot machine and test your luck!\nMoney betted on: {bet}",
        )

        await database.db.verify_user(str(interaction.user.id))
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
                f"You have too many coins in your account. Please keep it under {GAMBLING_LIMIT} coins."
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
        slot1 = random.choice(slot_emojis)  # Approximation for the slot visuals
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


async def setup(bot):
    await bot.add_cog(Gambling(bot))
