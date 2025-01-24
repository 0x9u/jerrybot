import discord


class HeistView(discord.ui.View):
    def __init__(self, user: discord.User, target_user: discord.User):
        super().__init__(timeout=30)
        # users in the heist
        self.users: list[discord.User] = [user]
        self.target_user = target_user

    @discord.ui.button(label="You son of a bitch, I'm in!", style=discord.ButtonStyle.green)
    async def heist(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if self.target_user.id == interaction.user.id:
            await interaction.followup.send("You can't join your own heist!", ephemeral=True)
            return

        if not any(user.id == interaction.user.id for user in self.users):
            self.users.append(interaction.user)
            await interaction.followup.send("You entered the heist!", ephemeral=True)
        else:
            await interaction.followup.send("You are already in the heist!", ephemeral=True)

