import discord
import database
import random
import asyncio
import traceback

from utils import jerrymon_calculate_damage, jerrymon_calculate_xp_earnt, ItemCode

# todo: show visuals

# todo: implement evade for speed
# todo: implement switch

# todo: fix moves

BASE_CAPTURE_CHANCE = 50


def get_alive_jerrymon(data: dict) -> int:
    return next((i for i, d in enumerate(data) if d.get("hp", 0) > 0), -1)


class JerrymonBattleView(discord.ui.View):
    def __init__(self, message: discord.Message, embed: discord.Embed, user: discord.User, opponent: discord.User = None):
        super().__init__(timeout=60)
        self.message = message
        self.embed = embed
        self.user = user

        self.opponent = opponent
        self.jerrymon_id = None

        self.current_turn = False  # user = True opponent = False

        self.selected_move = None

        self.is_opponent = self.opponent is not None

        self.opponent_party = []
        self.opponent_jerrymon_moves = []

        self.user_party = []
        self.jerrymon_moves = []

        self.selected_jerrymon: int = 0
        self.opponent_selected_jerrymon: int = 0

        self.dropdown: BattleMoveDropdown = None

    @classmethod
    async def create(
        cls,
        title,
        description,
        interaction: discord.Interaction,
        user: discord.User,
        opponent: discord.User = None,
        jerrymon_id: int = None,
    ):
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.blue())
        embed.add_field(
            name="Status", value="No action done yet.", inline=False)
        embed.add_field(
            name=user.name, value="Jerrymon not loaded in yet.", inline=True)
        embed.add_field(name="Opponent" if opponent is None else opponent.name,
                        value="Jerrymon not loaded in yet.", inline=True)
        message = await interaction.followup.send(embed=embed)
        view = cls(message, embed, user, opponent)

        # todo: implement selection for jerrymon in party
        if view.is_opponent:
            # ! assumes at least one alive
            view.opponent_party = await database.db.get_jerrymon_party(str(view.opponent.id))
            view.opponent_selected_jerrymon = get_alive_jerrymon(
                view.opponent_party)
            view.opponent_jerrymon_moves = [await database.db.get_jerrymon_known_moves(
                jerrymon["jerrymon_id"]) for jerrymon in view.opponent_party
            ]
        else:
            wild_jerrymon = await database.db.get_jerrymon_by_id(jerrymon_id)
            view.jerrymon_id = await database.db.add_jerrymon_to_inventory(str(view.user.id), wild_jerrymon["id"])
            print("JERRYMON INV ID", view.jerrymon_id)
            view.opponent_party = [await database.db.get_jerrymon_inventory_by_id(str(view.user.id), view.jerrymon_id)]
            # ! consider the case where its a evolved jerrymon
            view.opponent_jerrymon_moves = [await database.db.get_jerrymon_known_moves(
                view.jerrymon_id
            )]
            # only here for readability
            view.oppponent_selected_jerrymon = 0

        view.user_party = await database.db.get_jerrymon_party(str(view.user.id))
        view.selected_jerrymon = get_alive_jerrymon(view.user_party)
        view.jerrymon_moves = [await database.db.get_jerrymon_known_moves(
            jerrymon["id"]) for jerrymon in view.user_party]

        selected_jerrymon = view.user_party[view.selected_jerrymon]
        opponent_selected_jerrymon = view.opponent_party[view.opponent_selected_jerrymon]

        # determine who goes first by speed
        if selected_jerrymon["speed"] > opponent_selected_jerrymon["speed"]:
            view.current_turn = True
        elif selected_jerrymon["speed"] < opponent_selected_jerrymon["speed"]:
            view.current_turn = False
        else:
            view.current_turn = random.choice([True, False])

        view.dropdown = BattleMoveDropdown(
            view.jerrymon_moves[view.selected_jerrymon] if view.current_turn else view.opponent_jerrymon_moves[view.opponent_selected_jerrymon], view
        )

        view.add_item(view.dropdown)

        print("enemy moves", view.opponent_jerrymon_moves,
              "player moves", view.jerrymon_moves)

        view.embed.set_field_at(1, name=f"{view.user.name} - {selected_jerrymon['nickname'] or selected_jerrymon['jerrymons']['name']}",
                                value=f"HP: {selected_jerrymon['hp']}/{selected_jerrymon['max_hp']}", inline=True)
        view.embed.set_field_at(2, name=f"{view.opponent.name} - {opponent_selected_jerrymon['nickname'] or opponent_selected_jerrymon['jerrymons']['name']}"
                                if view.opponent is not None else opponent_selected_jerrymon['jerrymons']["name"],
                                value=f"HP: {opponent_selected_jerrymon['hp']}/{opponent_selected_jerrymon['max_hp']}", inline=True)

        await message.edit(embed=view.embed, view=view)

        if view.opponent is None and view.current_turn is False:
            await view.ai_move()

        return view

    async def update_message(self):
        selected_jerrymon = self.user_party[self.selected_jerrymon]
        opponent_selected_jerrymon = self.opponent_party[self.opponent_selected_jerrymon]
        self.embed.set_field_at(1, name=f"{self.user.name} - {selected_jerrymon['nickname'] or selected_jerrymon['jerrymons']['name']}",
                                value=f"HP: {selected_jerrymon['hp']}/{selected_jerrymon['max_hp']}", inline=True)
        self.embed.set_field_at(2, name=f"{self.opponent.name} - {opponent_selected_jerrymon['nickname'] or opponent_selected_jerrymon['jerrymons']['name']}"
                                if self.opponent is not None else opponent_selected_jerrymon['jerrymons']["name"],
                                value=f"HP: {opponent_selected_jerrymon['hp']}/{opponent_selected_jerrymon['max_hp']}", inline=True)

        await self.message.edit(embed=self.embed, view=self)

    async def save_data(self):
        # todo: check if jerrymon is wild
        for jerrymon in self.user_party + self.opponent_party:
            del jerrymon["jerrymons"]
            await database.db.save_jerrymon(jerrymon)

    async def ai_move(self):
        # disable all buttons
        for child in self.children:
            child.disabled = True
        await self.message.edit(embed=self.embed, view=self)

        await asyncio.sleep(2)

        # todo: decide whether to heal

        selected_move = random.choice(
            self.opponent_jerrymon_moves[self.opponent_selected_jerrymon])

        print("AI MOVE", selected_move)

        damage = jerrymon_calculate_damage(
            self.opponent_party[self.opponent_selected_jerrymon]["attack"],
            selected_move['jerrymons_moves']["power"],
            self.user_party[self.selected_jerrymon]["defense"]
        )

        self.user_party[self.selected_jerrymon]["hp"] -= damage

        jerrymon_died = self.user_party[self.selected_jerrymon]["hp"] <= 0

        if jerrymon_died:
            self.user_party[self.selected_jerrymon]["hp"] = 0

        if jerrymon_died:
            next_alive = get_alive_jerrymon(self.user_party)

            if next_alive == -1:
                self.embed.set_field_at(
                    0, name="Status", value="You lost the battle!", inline=False)

                await self.update_message()
                await self.save_data()
                return

            name_of_next_alive = self.user_party[next_alive]["jerrymons"][
                "name"] or self.user_party[next_alive]["jerrymons"]["nickname"]

            self.embed.set_field_at(0, name="Status",
                                    value=f"You switched out to {name_of_next_alive}!", inline=False)

            self.selected_jerrymon = next_alive
        else:
            self.embed.set_field_at(0, name="Status",
                                    value=f"{
                                        self.opponent_party[self.opponent_selected_jerrymon]['jerrymons']['name']} attacked you with {selected_move['jerrymons_moves']['name']}!", inline=False)

        self.current_turn = not self.current_turn

        for child in self.children:
            child.disabled = False

        await self.dropdown.update_dropdown()
        await self.update_message()

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.green)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.edit_message(content="You attacked Jerrymon!", view=None)
        try:

            await interaction.response.defer()

            # fix this check
            if (self.current_turn and self.user.id != interaction.user.id or
                    (not self.current_turn and self.opponent is not None and self.opponent.id != interaction.user.id)):
                await interaction.followup.send(content="It's not your turn!", ephemeral=True)
                return

            if self.selected_move is None:
                await interaction.followup.send(content="You have not selected a move!", ephemeral=True)
                return

            print("TRYING TO ATTACK JERRYMON")

            opponent_name = (
                self.opponent.name if self.opponent is not None else self.opponent_party[self.opponent_selected_jerrymon]["jerrymons"]["name"]) if self.current_turn else self.user.name

            # calculate chance to dodge/evade

            if random.random() > self.selected_move["jerrymons_moves"]["accuracy"]:

                self.embed.set_field_at(0, name="Status",
                                        value=f"{opponent_name} dodged the attack!", inline=False)

                # progress
                await self.update_message()

                self.current_turn = not self.current_turn

                if self.opponent is None:
                    await self.ai_move()

                return

            print("PASSed")

            selected_jerrymon = (
                self.user_party[self.selected_jerrymon] if self.current_turn else self.opponent_party[self.opponent_selected_jerrymon]
            )

            opponent_selected_jerrymon = (
                self.opponent_party[self.opponent_selected_jerrymon] if self.current_turn else self.user_party[self.selected_jerrymon]
            )

            # calculate damage

            damage = jerrymon_calculate_damage(
                selected_jerrymon["attack"],
                self.selected_move["jerrymons_moves"]["power"],
                opponent_selected_jerrymon["defense"]
            )

            opponent_selected_jerrymon["hp"] -= damage

            opponent_jerrymon_name = (
                (opponent_selected_jerrymon["nickname"] or opponent_selected_jerrymon["jerrymons"]["name"]) if self.current_turn else (
                    selected_jerrymon["nickname"] or selected_jerrymon["jerrymons"]["name"])
            )

            jerrymon_died = opponent_selected_jerrymon["hp"] <= 0

            if jerrymon_died:
                opponent_selected_jerrymon["hp"] = 0
                self.embed.set_field_at(0, name="Status",
                                        value=f"{opponent_jerrymon_name} fainted!", inline=False)
            else:
                # msg not being updated all the time
                self.embed.set_field_at(0, name="Status",
                                        value=f"{opponent_jerrymon_name} took {damage} damage!", inline=False)

            # update opponent
            if self.current_turn:
                self.opponent_party[self.opponent_selected_jerrymon] = opponent_selected_jerrymon
            else:
                self.user_party[self.selected_jerrymon] = opponent_selected_jerrymon

            print("PASSED 2")

            if jerrymon_died:
                next_alive = get_alive_jerrymon(
                    self.opponent_party if self.current_turn else self.user_party)
                if next_alive == -1:

                    winner = self.user.name if self.current_turn else (self.opponent.name if self.opponent is not None else self.opponent_party[
                        self.opponent_selected_jerrymon]["jerrymons"]["name"])
                    await interaction.followup.send(content=f"{winner} won the battle!")
                    await self.update_message()

                    # calculate xp earnt

                    # todo: consider case where multiple jerrymons died

                    if self.current_turn or self.opponent is not None:

                        xp = jerrymon_calculate_xp_earnt(
                            selected_jerrymon["level"],
                            opponent_selected_jerrymon["level"]
                        )

                        await interaction.followup.send(content=f"{winner} gained {xp} xp!")

                        if self.current_turn:
                            self.user_party[self.selected_jerrymon]["xp"] += xp
                        else:
                            self.opponent_party[self.opponent_selected_jerrymon]["xp"] += xp

                    for child in self.children:
                        child.disabled = True

                    await self.message.edit(embed=self.embed, view=self)

                    await self.save_data()
                    self.stop()

                    return

                if self.current_turn:
                    # show switched out msg
                    self.opponent_selected_jerrymon = next_alive
                else:
                    self.selected_jerrymon = next_alive

            self.current_turn = not self.current_turn

            await self.dropdown.update_dropdown()
            await self.update_message()

            self.selected_move = None

            # show log
            if self.opponent is None:
                await self.ai_move()

        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(
                "An error occurred while trying to attack the Jerrymon.", ephemeral=True
            )

    @discord.ui.button(label="Run", style=discord.ButtonStyle.red)
    async def run(self, interaction: discord.Interaction, button: discord.ui.Button):
        # add check if opponent
        await interaction.response.defer()
        if (self.current_turn and self.user.id != interaction.user.id or
                (not self.current_turn and self.opponent is not None and self.opponent.id != interaction.user.id)):
            await interaction.followup.send(content="It's not your turn!", ephemeral=True)
            return

        if self.opponent is not None:
            await interaction.followup.send(content="You cannot run from a battle!", ephemeral=True)
            return

        print("TEST")

        self.embed.set_field_at(
            0, name="Status", value="You ran from the Jerrymon!", inline=False)

        await self.message.edit(embed=self.embed, view=None)
        # save data

        await self.save_data()

        await database.db.remove_jerrymon_from_inventory(str(self.user.id), self.jerrymon_id)

        self.stop()

    # todo: expand this to use
    @discord.ui.button(label="Capture", style=discord.ButtonStyle.gray)
    async def capture(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()

            if self.opponent is not None:
                await interaction.followup.send(content="You can only capture wild jerrymons!", ephemeral=True)
                return

            jerrymon_balls = await database.db.get_item_inventory_by_id(str(interaction.user.id), ItemCode.JERRYMON_BALL.value)
            
            jerrymon_balls = jerrymon_balls[0] if jerrymon_balls is not None else None

            if jerrymon_balls is None:
                await interaction.followup.send(content="You don't have any jerrymon balls!", ephemeral=True)
                return

            await database.db.remove_item_from_inventory(str(interaction.user.id), jerrymon_balls["id"], 1)
            
            # calculate chance

            opponent_jerrymon = self.opponent_party[self.opponent_selected_jerrymon]

            speed_factor = 1 / (opponent_jerrymon["speed"] / 100)

            health_factor = (
                opponent_jerrymon["max_hp"] - opponent_jerrymon["hp"]) / opponent_jerrymon["max_hp"]

            capture_chance = BASE_CAPTURE_CHANCE * speed_factor * health_factor * 2

            capture_chance = min(0, max(100, capture_chance))

            if not random.uniform(0, 100) <= capture_chance:
                await interaction.followup.send(content="You failed to capture the Jerrymon!", ephemeral=True)
                await self.ai_move()
                return

            await self.save_data()
            # no need to do anything else, its already saved
            self.stop()
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(
                "An error occurred while trying to capture the Jerrymon.", ephemeral=True
            )

    # @discord.ui.button(label="Switch", style=discord.ButtonStyle.gray)
    # async def switch(self, interaction: discord.Interaction, button: discord.ui.Button):
    #    await interaction.response.defer()


class BattleMoveDropdown(discord.ui.Select):
    def __init__(self, moves: list[dict[str, str]],  parent: JerrymonBattleView):
        self.moves = moves
        print("MOVES", moves)
        self.parent = parent
        options = [
            discord.SelectOption(label=move["jerrymons_moves"]["name"]) for move in self.moves
        ]

        super().__init__(placeholder="Select a move",
                         min_values=1, max_values=1, options=options)

    async def update_dropdown(self):
        moves = self.parent.jerrymon_moves[self.parent.selected_jerrymon] if self.parent.current_turn else self.parent.opponent_jerrymon_moves[self.parent.opponent_selected_jerrymon]
        self.options = [
            discord.SelectOption(label=move["jerrymons_moves"]["name"]) for move in moves
        ]
        self.moves = moves

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        move = next(
            (move for move in self.moves if move["jerrymons_moves"]["name"] == self.values[0]), None)
        print("MOVE", move)
        if move is None:
            return

        self.parent.selected_move = move
        await interaction.followup.send(f"Move '{move['jerrymons_moves']['name']}' selected!", ephemeral=True)
