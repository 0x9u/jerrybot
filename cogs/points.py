import discord
from discord import app_commands
from discord.ext import commands
import time
import database
from utils import (
    get_emoji_count,
    get_emoji_multiplier,
    max_xp,
    EffectCode,
    ItemCode,
    IntOrAll,
)
import numpy as np
from views import HeistView
from shared import shared
from datetime import datetime, timedelta, timezone
import random

# points system

# 60 seconds
ROB_COOLDOWN = 60

# 2 hours
HEIST_COOLDOWN = 60 * 60 * 2


class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coin_rate = 1
        self.xp_rate = 5

        # cooldowns - not using discords built in cooldowns
        # cause I dont think I can run it manually (some commands can fail and cooldown can still occur)
        self.last_msg_time: dict[str, int] = {}
        self.last_rob_time: dict[str, int] = {}
        self.last_heist_time: dict[str, int] = {}

        self.super_saiyan_mode: dict[str, int] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user_id = str(message.author.id)

        new_count = get_emoji_count(message.content)

        if new_count > 0:
            await database.db.verify_user(user_id)

            await database.db.update_leaderboard(user_id, new_count)
            await database.db.update_leaderboard_guild(user_id, message.guild.id, new_count)

            ratelimit = await database.db.get_user_ratelimit(user_id)
            current_time = time.time()

            if (
                user_id in self.super_saiyan_mode
                and current_time - self.super_saiyan_mode[user_id] > 60
            ):
                del self.super_saiyan_mode[user_id]

            if (
                current_time - self.last_msg_time.get(user_id, 0) >= ratelimit
                or user_id in self.super_saiyan_mode
            ):
                self.last_msg_time[user_id] = current_time

                toxicity = round(get_emoji_multiplier(message.content))

                if toxicity >= 2 and user_id not in self.super_saiyan_mode:
                    await message.channel.send(
                        f"Nice {message.author.name}, you got {toxicity}x coins and xp for that message."
                    )

                highest = await database.db.get_leaderboard_highest()

                buff = await database.db.get_buff(user_id)
                expired = False
                if buff:
                    time_created = datetime.fromisoformat(buff[0]["time_created"])
                    if time_created + timedelta(hours=2) < datetime.now(timezone.utc):
                        expired = True
                        await database.db.delete_buff(user_id)

                coins_multiplier = (
                    buff[0]["coins_multiplier"] if buff and not expired else 1
                )
                xp_multiplier = buff[0]["xp_multiplier"] if buff and not expired else 1
                super_saiyan_multiplier = 2 if user_id in self.super_saiyan_mode else 1

                if buff and not expired:
                    xp_msg = (
                        f"{buff[0]["xp_multiplier"]}x xp multiplier"
                        if buff[0]["xp_multiplier"] > 1
                        else ""
                    )
                    coins_msg = (
                        f"{buff[0]['coins_multiplier']}x coins multiplier"
                        if buff[0]["coins_multiplier"] > 1
                        else ""
                    )
                    if user_id not in self.super_saiyan_mode:
                        await message.channel.send(
                            f"{xp_msg}{' ' if xp_msg and coins_msg else ''}{coins_msg} for buff {message.author.name}"
                        )

                king_multiplier = 2 if highest and highest["user_id"] == user_id else 1
                if (
                    highest
                    and highest["user_id"] == user_id
                    and user_id not in self.super_saiyan_mode
                ):
                    await message.channel.send(
                        f"2x multiplier for king {message.author.name}"
                    )

                await database.db.update_user_coins(
                    user_id,
                    self.coin_rate
                    * toxicity
                    * king_multiplier
                    * coins_multiplier
                    * super_saiyan_multiplier,
                )
                if await database.db.update_user_xp(
                    user_id,
                    self.xp_rate
                    * toxicity
                    * king_multiplier
                    * xp_multiplier
                    * super_saiyan_multiplier,
                ):
                    await message.channel.send(
                        f"Congrats {message.author.mention}, you leveled up!"
                    )

                if (
                    await database.db.get_allowed_channel(
                        str(message.guild.id), str(message.channel.id)
                    )
                    and np.random.random() < 0.05
                    and user_id not in self.super_saiyan_mode
                ):
                    embed = discord.Embed(
                        title="Super Saiyan",
                        description=f"Quick, {message.author.mention} spam as much as you can in 1 minute!\nYou get a extra 2x multiplier (xp and coins) for each message.\nNote: the bots messages will not show.",
                        color=discord.Color.green(),
                    )
                    await message.channel.send(embed=embed)
                    self.super_saiyan_mode[user_id] = time.time()

                await database.db.update_user_xp(user_id, 0)
                await database.db.update_user_coins(user_id, 0)

    @app_commands.command(name="count", description="Display the count of the user.")
    @app_commands.describe(user="The user to check the count of.")
    async def count(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        if not user:
            user = interaction.user
        user_id = str(user.id)
        await database.db.verify_user(user_id)
        count = await database.db.get_user_word_count(user_id)
        embed = discord.Embed(
            title="Emoji count",
            description=f"{user.name}, you have {count}",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="level", description="Display the level of the user.")
    @app_commands.describe(user="The user to check the level of.")
    async def level(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        if not user:
            user = interaction.user
        user_id = str(user.id)
        await database.db.verify_user(user_id)
        level = await database.db.get_user_level(user_id)
        embed = discord.Embed(
            title="Level",
            description=f"{user.name}, you are level {level} with {await database.db.get_user_xp(user_id)}/{max_xp(level)} XP.",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="coins", description="Display the coins of the user.")
    @app_commands.describe(user="The user to check the coins of.")
    async def coins(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        if not user:
            user = interaction.user
        user_id = str(user.id)
        await database.db.verify_user(user_id)
        coins = await database.db.get_user_coins(user_id)
        embed = discord.Embed(
            title="Coins",
            description=f"{user.name}, you have {coins} coins.",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="bank", description="Display the coins of the user's bank."
    )
    @app_commands.describe(user="The user to check the bank coins of.")
    async def bank(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        if not user:
            user = interaction.user
        user_id = str(user.id)
        await database.db.verify_user(user_id)
        coins = await database.db.get_bank_coins(user_id)
        maxCoins = await database.db.get_max_bank_coins(user_id)
        embed = discord.Embed(
            title="Bank",
            description=f"{user.name}, you have {coins}/{maxCoins} coins in the bank.",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(
            embed=embed
        )

    @app_commands.command(
        name="balance", description="Display the coins and bank coins of the user."
    )
    @app_commands.describe(user="The user to check the balance of.")
    async def balance(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer()

        if not user:
            user = interaction.user
        user_id = str(user.id)
        await database.db.verify_user(user_id)
        coins = await database.db.get_user_coins(user_id)
        bankCoins = await database.db.get_bank_coins(user_id)
        maxBankCoins = await database.db.get_max_bank_coins(user_id)
        embed = discord.Embed(
            title="Balance",
            description=f"{user.name}, you have {coins} coins and {bankCoins}/{maxBankCoins} coins in the bank.",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="deposit", description="Deposit coins to the bank.")
    @app_commands.describe(amount="The amount of coins to deposit.")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        """
        Deposits a specified amount of coins from the user's balance to their bank account.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that triggered the command.
        amount : int
            The amount of coins to deposit into the bank.

        Sends a follow-up message if the user doesn't have enough coins in their balance
        to make the deposit or if the deposit would exceed the maximum bank coins allowed.
        """
        await interaction.response.defer()

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer.")
            return

        user_id = str(interaction.user.id)

        amount: int = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(user_id)
        )

        if amount < 1:
            await interaction.followup.send("Amount must be greater than 0.")
            return

        await database.db.verify_user(user_id)
        coins = await database.db.get_user_coins(user_id)
        if coins < amount:
            await interaction.followup.send(
                f"You don't have enough coins to deposit {amount}."
            )
            return
        coinsBank = await database.db.get_bank_coins(user_id)
        maxCoins = await database.db.get_max_bank_coins(user_id)
        if amount + coinsBank > maxCoins:
            await interaction.followup.send(
                f"You can't deposit more than {maxCoins} coins to the bank."
            )
            return
        await database.db.update_user_coins(user_id, -amount)
        await database.db.update_bank_coins(user_id, amount)
        await interaction.followup.send(f"Deposited {amount} coins to the bank.")

    @app_commands.command(name="withdraw", description="Withdraw coins from the bank.")
    @app_commands.describe(amount="The amount of coins to withdraw.")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        await interaction.response.defer()

        user_id = str(interaction.user.id)

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer.")
            return

        amount: int = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_bank_coins(user_id)
        )

        if amount < 1:
            await interaction.followup.send("Amount must be greater than 0.")
            return

        await database.db.verify_user(user_id)
        coins = await database.db.get_bank_coins(user_id)
        if coins < amount:
            await interaction.followup.send(
                f"You don't have enough coins in the bank to withdraw {amount}."
            )
            return
        await database.db.update_bank_coins(user_id, -amount)
        await database.db.update_user_coins(user_id, amount)
        await interaction.followup.send(f"Withdrew {amount} coins from the bank.")

    @app_commands.command(
        name="transfer", description="Transfer coins to another user."
    )
    @app_commands.describe(
        user="The user to transfer coins to.", amount="The amount of coins to transfer."
    )
    async def transfer(
        self, interaction: discord.Interaction, user: discord.User, amount: str
    ):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        target_id = str(user.id)

        try:
            parsed_amount = IntOrAll(amount)
        except ValueError:
            await interaction.followup.send("Amount must be an integer.")
            return

        amount = (
            parsed_amount.value
            if parsed_amount.value != "all"
            else await database.db.get_user_coins(user_id)
        )

        if amount < 1:
            await interaction.followup.send("Amount must be greater than 0.")
            return

        if user_id == target_id:
            await interaction.followup.send("You can't transfer coins to yourself.")
            return

        await database.db.verify_user(user_id)
        await database.db.verify_user(target_id)
        coins = await database.db.get_user_coins(user_id)

        if coins < amount:
            await interaction.followup.send(
                f"You don't have enough coins to transfer {amount}."
            )
            return

        await database.db.update_user_coins(user_id, -amount)
        await database.db.update_user_coins(target_id, amount)
        await interaction.followup.send(f"Transferred {amount} coins to {user.name}.")

    @app_commands.command(name="rob", description="Rob coins from another user.")
    @app_commands.describe(user="The user to rob coins from.")
    async def rob(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        target_id = str(user.id)

        if user_id == target_id:
            await interaction.followup.send("You can't rob coins from yourself.")
            return

        if str(self.bot.user.id) == target_id:
            await interaction.followup.send("You can't rob coins from the bot.")
            return

        if target_id in shared.rob_lock:
            await interaction.followup.send("You can't rob this user right now.")
            return

        # check cooldown
        if (
            user_id in self.last_rob_time
            and time.time() - self.last_rob_time[user_id] < ROB_COOLDOWN
        ):
            await interaction.followup.send(
                f"You can't rob again for {ROB_COOLDOWN - int(time.time() -self.last_rob_time[user_id])} seconds."
            )
            return

        await database.db.verify_user(user_id)
        await database.db.verify_user(target_id)
        target_coins = await database.db.get_user_coins(target_id)

        if target_coins == 0:
            await interaction.followup.send(f"{user.name} has no coins to rob.")
            return

        protected = await database.db.get_protection(target_id)
        if protected:
            chance_of_death = np.random.randint(1, 100)
            if chance_of_death <= 25:
                await interaction.followup.send(f"You died while robbing {user.name}.")
                coins = await database.db.get_user_coins(user_id)
                await database.db.update_user_coins(user_id, -coins)
            else:
                await interaction.followup.send(
                    f"You noticed {user.name} placed a bear trap and fled."
                )
            self.last_rob_time[user_id] = time.time()
            await database.db.update_protection(target_id, False)
            return

        equipped = await database.db.get_equipped(user_id)
        gun_id = equipped["gun_id"]
        effect = await database.db.get_item_effect(gun_id, EffectCode.ROB.value) if gun_id else 50

        # 20 chances
        chance = np.random.randint(1, 100, 20)
        amount = np.random.randint(1, target_coins + 1)
        try:
            if np.any(chance % effect == 0):
                await database.db.update_user_coins(user_id, amount)
                await database.db.update_user_coins(target_id, -amount)
                await interaction.followup.send(
                    f"You robbed {user.name} and got {amount} coins."
                )
            else:
                await interaction.followup.send(f"You failed to rob {user.name}.")

            # add cooldown
            self.last_rob_time[user_id] = time.time()
        except Exception as e:
            print(e)

    @app_commands.command(name="heist", description="Start a heist on someones bank.")
    @app_commands.describe(user="The user to start a heist on.")
    async def heist(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        target_id = str(user.id)

        if user_id == target_id:
            await interaction.followup.send("You start a heist on yourself.")
            return

        if target_id in shared.heists:
            await interaction.followup.send(f"{user.name} is already being heisted.")
            return

        if str(self.bot.user.id) == target_id:
            await interaction.followup.send("You can't start a heist on the bot.")
            return


        if (
            target_id in self.last_heist_time
            and time.time() - self.last_heist_time[target_id] < HEIST_COOLDOWN
        ):
            await interaction.followup.send(
                f"{user.name} has been heisted recently.\nYou can't heist them for {HEIST_COOLDOWN - int(time.time() - self.last_heist_time[target_id])} seconds."
            )
            return
        elif target_id in self.last_heist_time:
            del self.last_heist_time[target_id]
            return

        await database.db.verify_user(user_id)
        await database.db.verify_user(target_id)
        target_stuff = (
            await database.db.get_bank_coins(target_id)
            + await database.db.get_farms(target_id)
            + await database.db.get_slaves(target_id)
            + await database.db.get_mines(target_id)
            + sum([row["shares"] for row in await database.db.get_user_portfolio(target_id)])
        )

        if target_stuff == 0:
            await interaction.followup.send(f"{user.name} has nothing to heist.")
            return

        view = HeistView(interaction.user, user)

        embed = discord.Embed(
            title="Heist",
            description=f"{interaction.user.name} started a heist on {user.name}\nThe heist requires at least 4 players.\nThe more people join, the higher the chance of success.\nClick the button to join the heist",
            color=discord.Color.green(),
        )

        shared.heists.add(target_id)

        # dm target user about the heist
        dm_embed = discord.Embed(
            title="Heist",
            description=f"You are being heisted right now!",
            color=discord.Color.red()
        )
        try:
            await user.send(embed=dm_embed)
        except Exception as e:
            print(e)

        await interaction.followup.send(embed=embed, view=view)

        await view.wait()

        # have a check to see if heist still exists
        # if not then the user has called the cops

        if target_id not in shared.heists:
            # silently exit
            return

        if len(view.users) < 4:
            await interaction.followup.send("Not enough players to start a heist.")
            shared.heists.remove(target_id)
            return

        bodyguards = await database.db.get_bodyguards(target_id)
        if bodyguards > 0:
            await interaction.followup.send("A bodyguard stopped the heist.")
            await database.db.update_bodyguards(target_id, -1)
            shared.heists.remove(target_id)
            return

        chance = np.random.randint(1, 100, len(view.users))

        embed = discord.Embed(
            title="Heist Summary",
            description=f"Players joined the heist: {', '.join([user.name for user in view.users])}",
            color=discord.Color.green(),
        )

        for i, robber in enumerate(view.users):

            await database.db.verify_user(str(robber.id))

            equipped = await database.db.get_equipped(str(robber.id))
            gun_id = equipped["gun_id"]
            effect = await database.db.get_item_effect(gun_id, EffectCode.ROB.value) if gun_id else 50

            level = await database.db.get_user_level(str(robber.id))

            coins = await database.db.get_bank_coins(target_id)
            heist_coins = np.random.randint(1, coins + 1) if coins > 0 else 0

            slaves = await database.db.get_slaves(target_id)
            heist_slaves = np.random.randint(1, slaves + 1) if slaves > 0 else 0

            farm_level = (await database.db.get_item_by_id(ItemCode.FARM.value))["level_require"]
            farms = await database.db.get_farms(target_id)
            heist_farms = (
                np.random.randint(1, farms + 1)
                if farms > 0 and level >= farm_level
                else 0
            )

            mine_level = (await database.db.get_item_by_id(ItemCode.MINE.value))["level_require"]
            mines = await database.db.get_mines(target_id)
            heist_mines = (
                np.random.randint(1, mines + 1)
                if mines > 0 and level >= mine_level
                else 0
            )

            portfolio = await database.db.get_user_portfolio(target_id)
            chosen_share = random.choice(portfolio) if portfolio else None
            heist_shares = (
                np.random.randint(1, chosen_share["shares"] + 1)
                if chosen_share is not None
                else 0
            )

            if chance[i] % effect == 0:
                await database.db.update_bank_coins(target_id, -heist_coins)
                await database.db.update_user_coins(str(robber.id), heist_coins)

                await database.db.update_slaves(target_id, -heist_slaves)
                await database.db.update_slaves(str(robber.id), heist_slaves)

                await database.db.update_farms(target_id, -heist_farms)
                await database.db.update_farms(str(robber.id), heist_farms)

                await database.db.update_mines(target_id, -heist_mines)
                await database.db.update_mines(str(robber.id), heist_mines)

                if heist_shares:
                    await database.db.update_user_portfolio(
                        target_id, chosen_share["symbol"], -heist_shares
                    )
                    await database.db.update_user_portfolio(
                       str(robber.id), chosen_share["symbol"], heist_shares
                    )

                embed.add_field(
                    name=f"{view.users[i].name}",
                    value=(
                        f"Robbed {user.name}\n"
                        f"Received {heist_coins} coins.\n"
                        f"Received {heist_slaves} slaves.\n"
                        f"Received {heist_farms} farms.\n"
                        f"Received {heist_mines} mines"
                        + (f"\nReceived {heist_shares} of {chosen_share["symbol"]}"
                        if heist_shares
                        else "")
                    ),
                    inline=False,
                )
            else:
                embed.add_field(
                    name=f"{view.users[i].name}",
                    value=f"Failed to rob {user.name}",
                    inline=False,
                )

        await interaction.followup.send(embed=embed)
        self.last_heist_time[target_id] = time.time()
        shared.heists.remove(target_id)


async def setup(bot):
    await bot.add_cog(Points(bot))
