import discord
import database
import random
import asyncio

from utils import jerrymon_calculate_damage, ItemCode

# todo: show visuals

# todo: implement evade for speed
# todo: implement switch


def get_alive_jerrymon(data: dict) -> int:
    return next((i for i, d in enumerate(data) if d.get("id") == 2), -1)


class JerrymonBattleView(discord.ui.View):
    def __init__(self, message: discord.Message, embed: discord.Embed, user: discord.User, opponent: discord.User = None):
        super().__init__(timeout=60)
        self.message = message
        self.embed = embed
        self.user = user

        self.opponent = opponent
        self.jerrymon_id = jerrymon_id

        self.current_turn = False  # user = True opponent = False

        self.selected_move = None

        self.is_opponent = self.opponent is not None

        self.opponent_party = []
        self.opponent_jerrymon_moves = []

        self.user_party = []
        self.jerrymon_moves = []

        self.selected_jerrymon: int = 0
        self.opponent_selected_jerrymon: int = 0

        self.dropdown : BattleMoveDropdown = None

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
            name="Status", value="No action done yet.", inline=True)
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
            view.opponent_selected_jerrymon_moves = [await database.db.get_jerrymon_known_moves(
                jerrymon["jerrymon_id"]) for jerrymon in view.opponent_party
            ]
        else:
            wild_jerrymon = await database.db.get_jerrymon_by_id(jerrymon_id)
            view.jerrymon_id = await database.db.add_jerrymon_to_inventory(str(view.user.id), wild_jerrymon["id"])
            view.opponent_party = [await database.db.get_jerrymon_inventory_by_id(str(view.user.id), view.jerrymon_id)]
            # ! consider the case where its a evolved jerrymon
            view.opponent_selected_jerrymon_moves = [database.db.get_jerrymon_move_tree_by_lvl(
                view.jerrymon_id, 1)]
            # only here for readability
            view.oppponent_selected_jerrymon = 0

        view.user_party = await database.db.get_jerrymon_party(str(view.user.id))
        view.selected_jerrymon = get_alive_jerrymon(view.user_party)
        view.selected_jerrymon_moves = [await database.db.get_jerrymon_known_moves(
            jerrymon["jerrymon_id"]) for jerrymon in view.user_party]

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
            view.selected_jerrymon_moves if view.current_turn else view.opponent_selected_jerrymon_moves
        )

        view.add_item(view.dropdown)

        view.embed.set_field_at(1, name=view.user.name,
                                value=f"HP: {view.selected_jerrymon['hp']}/{view.selected_jerrymon['max_hp']}", inline=True)
        view.embed.set_field_at(2, name=view.opponent.name if view.opponent is not None else view.selected_jerrymon["name"],
                                value=f"HP: {view.opponent_selected_jerrymon['hp']}/{view.opponent_selected_jerrymon['max_hp']}", inline=True)

        await message.edit(embed=view.embed, view=view)
        return view

    async def update_message(self):
        self.embed.set_field_at(1, name=self.user.name,
                                value=f"HP: {self.selected_jerrymon['hp']}/{self.selected_jerrymon['max_hp']}", inline=True)
        self.embed.set_field_at(2, name=(
            self.opponent.name if self.opponent is not None else self.opponent_selected_jerrymon["name"]),
            value=f"HP: {self.opponent_selected_jerrymon['hp']}/{self.opponent_selected_jerrymon['max_hp']}", inline=True)

        await self.message.edit(embed=self.embed, view=self)

    async def save_data(self):
        # todo: check if jerrymon is wild
        for jerrymon in self.user_party + self.opponent_party:
            await database.db.save_jerrymon(jerrymon)

    async def ai_move(self):
        # disable all buttons
        for child in self.children:
            child.disabled = True
        await self.message.edit(embed=self.embed, view=self)

        await asyncio.sleep(2)

        for child in self.children:
            child.disabled = False
        await self.message.edit(embed=self.embed, view=self)

        # todo: decide whether to heal

        selected_move = random.choice(self.selected_jerrymon_moves)

        damage = jerrymon_calculate_damage(
            self.opponent_selected_jerrymon["attack"],
            selected_move["power"],
            self.selected_jerrymon["defense"]
        )

        self.selected_jerrymon["hp"] -= damage

        jerrymon_died = False

        if self.selected_jerrymon["hp"] <= 0:
            self.selected_jerrymon["hp"] = 0
            jerrymon_died = True

        await self.update_message()

        if jerrymon_died:
            next_alive = get_alive_jerrymon(self.user_party)

            if next_alive == -1:
                self.embed.set_field_at(
                    0, name="Status", value="You lost the battle!", inline=True)
                await self.message.edit(embed=self.embed, view=None)
                await self.save_data()
                return

            name_of_next_alive = self.user_party[next_alive]["name"]

            self.embed.set_field_at(0, name="Status",
                                    value=f"You switched out to {name_of_next_alive}!", inline=True)

            self.selected_jerrymon = next_alive
        else:
            self.embed.set_field_at(0, name="Status",
                                    value=f"{self.opponent_selected_jerrymon['name']} attacked you with {selected_move['name']}!", inline=True)

        self.current_turn = not self.current_turn

    @discord.ui.button(label="Attack", style=discord.ButtonStyle.green)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.edit_message(content="You attacked Jerrymon!", view=None)

        await interaction.response.defer()

        if (self.current_turn and self.user.id != interaction.user.id or
                (not self.current_turn and self.opponent is not None and self.opponent.id != interaction.user.id)):
            await interaction.followup.send(content="It's not your turn!", ephemeral=True)
            return

        if self.selected_move is None:
            await interaction.followup.send(content="You have not selected a move!", ephemeral=True)
            return

        opponent_name = (
            self.opponent.name if self.opponent is not None else self.opponent_party[self.opponent_selected_jerrymon]["name"]) if self.current_turn else self.user.name

        # calculate chance to dodge/evade

        if random.random() < self.selected_move["accuracy"]:

            self.embed.set_field_at(0, name="Status",
                                    value=f"{opponent_name} dodged the attack!", inline=True)

            # progress
            await self.update_message()

            self.current_turn = not self.current_turn

            if self.opponent is not None:
                await self.ai_move()

            return

        selected_jerrymon = (
            self.user_party[self.selected_jerrymon] if self.current_turn else self.opponent_party[self.opponent_selected_jerrymon]
        )

        opponent_selected_jerrymon = (
            self.opponent_party[self.opponent_selected_jerrymon] if self.current_turn else self.user_party[self.selected_jerrymon]
        )

        # calculate damage

        damage = jerrymon_calculate_damage(
            selected_jerrymon["attack"],
            self.selected_move["power"],
            opponent_selected_jerrymon["defense"]
        )

        opponent_selected_jerrymon["hp"] -= damage

        opponent_jerrymon_name = (
            self.opponent_selected_jerrymon["name"] if self.current_turn else self.selected_jerrymon["name"]
        )

        jerrymon_died = False

        if opponent_selected_jerrymon["hp"] <= 0:
            opponent_selected_jerrymon["hp"] = 0

            self.embed.set_field_at(0, name="Status",
                                    value=f"{opponent_jerrymon_name} fainted!", inline=True)

            jerrymon_died = True
        else:
            self.embed.set_field_at(0, name="Status",
                                    value=f"{opponent_jerrymon_name} took {damage} damage!", inline=True)

        # update opponent
        if self.current_turn:
            self.opponent_selected_jerrymon[self.opponent_selected_jerrymon] = opponent_selected_jerrymon
        else:
            self.selected_jerrymon[self.selected_jerrymon] = opponent_selected_jerrymon

        await self.update_message()

        if jerrymon_died:
            next_alive = get_alive_jerrymon(
                self.opponent_party if self.current_turn else self.user_party)
            if next_alive == -1:
                await self.save_data()

                winner = self.opponent if self.current_turn else self.user
                await interaction.followup.send(content=f"{winner.name} won the battle!", ephemeral=True)

                self.stop()
                return

            if self.current_turn:
                self.opponent_selected_jerrymon = next_alive
            else:
                self.selected_jerrymon = next_alive

        self.current_turn = not self.current_turn
        await self.dropdown.update_dropdown()

        # show log
        if self.opponent is not None:
            await self.ai_move()

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

        await interaction.response.edit_message(content="You ran from Jerrymon!", view=None)
        # save data

        await self.save_data()

        await database.db.remove_jerrymon_from_inventory(str(self.user.id), self.jerrymon_id)

        await self.stop()

    # todo: expand this to use
    @discord.ui.button(label="Capture", style=discord.ButtonStyle.gray)
    async def capture(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if self.opponent is not None:
            await interaction.followup.send(content="You can only capture wild jerrymons!", ephemeral=True)
            return

        jerrymon_balls = await database.db.get_item_inventory_count(str(interaction.user.id), ItemCode.JERRYMON_BALL.value)

        if jerrymon_balls < 1:
            await interaction.followup.send(content="You don't have any jerrymon balls!", ephemeral=True)
            return

        await database.db.update_item_inventory_count(str(interaction.user.id), ItemCode.JERRYMON_BALL.value, -1)

        await self.save_data()
        # no need to do anything else, its already saved
        await self.stop()

    # @discord.ui.button(label="Switch", style=discord.ButtonStyle.gray)
    # async def switch(self, interaction: discord.Interaction, button: discord.ui.Button):
    #    await interaction.response.defer()


class BattleMoveDropdown(discord.ui.Select):
    def __init__(self, moves: list[dict[str, str]],  parent: JerrymonBattleView):
        self.moves = moves
        self.parent = parent
        options = [
            discord.SelectOption(label=move["name"]) for move in self.moves
        ]

        super().__init__(placeholder="Select a move",
                         min_values=1, max_values=1, options=options)

    async def update_dropdown(self):
        moves = self.parent.jerrymon_moves[self.parent.selected_jerrymon] if self.parent.current_turn else self.parent.opponent_jerrymon_moves[self.parent.opponent_selected_jerrymon]
        self.options = [
            discord.SelectOption(label=move["name"]) for move in moves
        ]

    async def callback(self, interaction: discord.Interaction):
        move = next(
            (move for move in self.moves if move["name"] == self.values[0]), None)
        if move is None:
            return

        self.parent.selected_move = move
