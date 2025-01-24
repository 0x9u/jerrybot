import discord
import database
import random

# todo: show visuals

# todo: implement evade for speed

class JerrymonBattleView(discord.ui.View):
    def __init__(self, message: discord.Message, embed: discord.Embed, user: discord.User, opponent: discord.User = None, jerrymon_id: int = None):
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
        self.user_party = []

        self.selected_jerrymon = None
        self.selected_jerrymon_moves = None

        self.opponent_selected_jerrymon = None
        self.opponent_selected_jerrymon_moves = None

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
        embed.add_field(name="Status", value="No action done yet.", inline=True)
        embed.add_field(name=user.name, value="Jerrymon not loaded in yet.", inline=True)
        embed.add_field(name="Opponent" if opponent is None else opponent.name, value="Jerrymon not loaded in yet.", inline=True)
        message = await interaction.followup.send(embed=embed)
        view = cls(message, embed, user, opponent, jerrymon_id)

        # todo: implement selection for jerrymon in party
        if view.is_opponent:
            # ! assumes at least one alive
            view.opponent_party = await database.db.get_jerrymon_party(str(view.opponent.id))
            view.opponent_selected_jerrymon = (await database.db.get_alive_jerrymons(view.opponent.id))[0]
            view.opponent_selected_jerrymon_moves = database.db.get_jerrymon_known_moves(
                view.opponent_selected_jerrymon["id"])
        else:
            view.opponent_party = [await database.db.get_jerrymon_by_id(view.jerrymon_id)]
            # ! consider the case where its a evolved jerrymon
            view.opponent_selected_jerrymon_moves = database.db.get_jerrymon_move_tree_by_lvl(
                view.jerrymon_id, 1)

        view.user_party = await database.db.get_jerrymon_party(str(view.user.id))
        view.selected_jerrymon = (await database.db.get_alive_jerrymons(view.user.id))[0]
        view.selected_jerrymon_moves = database.db.get_jerrymon_known_moves(
            view.selected_jerrymon["id"])

        # determine who goes first by speed
        if view.selected_jerrymon["speed"] > view.opponent_selected_jerrymon["speed"]:
            view.current_turn = True
        elif view.selected_jerrymon["speed"] < view.opponent_selected_jerrymon["speed"]:
            view.current_turn = False
        else:
            view.current_turn = random.choice([True, False])

        await message.edit(embed=view.embed, view=view)
        return view

    async def update_message(self):
        await self.message.edit(embed=self.embed, view=self)

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
        
        # calculate chance to dodge/evade
        
        # calculate damage
        
        # show log
        

    @discord.ui.button(label="Run", style=discord.ButtonStyle.red)
    async def run(self, interaction: discord.Interaction, button: discord.ui.Button):
        # add check if opponent
        await interaction.response.defer()
        if (self.current_turn and self.user.id != interaction.user.id  or 
                (not self.current_turn and self.opponent is not None and self.opponent.id != interaction.user.id)):
            await interaction.followup.send(content="It's not your turn!", ephemeral=True)
            return
        
        await interaction.response.edit_message(content="You ran from Jerrymon!", view=None)
        # save data
        await self.stop()

    @discord.ui.button(label="block", style=discord.ButtonStyle.gray)
    async def block(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="You blocked Jerrymon!", view=None)

    # todo: expand this to use
    @discord.ui.button(label="Capture", style=discord.ButtonStyle.gray)
    async def capture(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="You captured Jerrymon!", view=None)
    
    @discord.ui.button(label="Switch", style=discord.ButtonStyle.gray)
    async def switch(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class BattleMoveDropdown(discord.ui.Select):
    def __init__(self, moves: list[dict[str, str]],  parent: JerrymonBattleView):
        self.moves = moves
        self.parent = parent
        options = [
            discord.SelectOption(label=move["name"]) for move in self.moves
        ]

        super().__init__(placeholder="Select a move",
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        move = next(
            (move for move in self.moves if move["name"] == self.values[0]), None)
        if move is None:
            return

        self.parent.selected_move = move
