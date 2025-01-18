import discord

RED_EMOJI = "🔴"
YELLOW_EMOJI = "🟡"
BLACK_EMOJI = "⚫"


class Connect4View(discord.ui.View):
    def __init__(self, user1: discord.User, user2: discord.User, embed: discord.Embed, message: discord.Message):
        super().__init__(timeout=120)
        self.user1 = user1
        self.user2 = user2
        self.embed = embed
        self.message = message

        # turn
        self.user1_turn = True

        self.state = [[0 for _ in range(7)] for _ in range(6)]

        for i in range(6):
            embed.add_field(name="", value="".join([BLACK_EMOJI for _ in range(7)]), inline=False)


        for i in range(7):
            self.add_item(self.create_button(i))
        
        # 0 = no winner, 1 = user1, 2 = user2
        self.winner = 0
    
    
    def check_column_free(self, col: int) -> int:
        # get lowest column free
        for row in range(5, -1, -1):
            if self.state[row][col] == 0: 
                return row
        return -1
    
    async def render_game(self):
        # get each column of each row and render one by one
        # in embed

        for row in range(6):
            row_col = ""
            for col in range(7):
                if self.state[row][col] == 0:
                    row_col += BLACK_EMOJI
                elif self.state[row][col] == 1:
                    row_col += RED_EMOJI
                else:
                    row_col += YELLOW_EMOJI
            self.embed.set_field_at(row, name="", value=row_col, inline=False)

        await self.message.edit(embed=self.embed, view=self)
    
    def check_win(self) -> int:
        # check horizontal
        for row in range(6):
            for col in range(4):
                if (
                    self.state[row][col] == self.state[row][col + 1]
                    == self.state[row][col + 2]
                    == self.state[row][col + 3]
                    != 0
                ):
                    return self.state[row][col]

        # check vertical
        for col in range(7):
            for row in range(3):
                if (
                    self.state[row][col] == self.state[row + 1][col]
                    == self.state[row + 2][col]
                    == self.state[row + 3][col]
                    != 0
                ):
                    return self.state[row][col]

        # check diagonal
        for row in range(3):
            for col in range(4):
                if (
                    self.state[row][col] == self.state[row + 1][col + 1]
                    == self.state[row + 2][col + 2]
                    == self.state[row + 3][col + 3]
                    != 0
                ):
                    return self.state[row][col]

        for row in range(3):
            for col in range(3, 7):
                if (
                    self.state[row][col] == self.state[row + 1][col - 1]
                    == self.state[row + 2][col - 2]
                    == self.state[row + 3][col - 3]
                    != 0
                ):
                    return self.state[row][col]

        return 0

    def check_draw(self) -> bool:
        for row in range(6):
            for col in range(7):
                if self.state[row][col] == 0:
                    return False
        return True


    def create_button(self, column):
        button = discord.ui.Button(label=str(column + 1), style=discord.ButtonStyle.primary)

        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()

            if (
                self.user1_turn
                and interaction.user.id != self.user1.id
                or not self.user1_turn
                and interaction.user.id != self.user2.id
            ):
                await interaction.followup.send("It's not your turn!", ephemeral=True)
                return

            row = self.check_column_free(column)
            if row == -1:
                await interaction.followup.send("Column is full!", ephemeral=True)
                return

            self.state[row][column] = 1 if self.user1_turn else 2

            await self.render_game()

            if (winner := self.check_win()) != 0:
                await interaction.followup.send(f"{self.user1 if winner == 1 else self.user2} won!")
                self.winner = winner
                self.stop()
                return
            
            if self.check_draw():
                await interaction.followup.send("It's a draw!")
                self.stop()
                return

            self.user1_turn = not self.user1_turn

        button.callback = callback
        return button
    
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.danger)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.id not in [self.user1.id, self.user2.id]:
            await interaction.followup.send("You are not in the game!", ephemeral=True)
            return
        await interaction.followup.send("Game ended.")
        self.stop()