import discord
from discord.ui import View, Button
import traceback

class PaginationView(View):
    @classmethod
    async def create(
        cls,
        data,
        title,
        description,
        interaction: discord.Interaction,
        inline=False,
        color: discord.Color = discord.Color.blue(),
    ):
        embed = discord.Embed(title=title, description=description)
        message = await interaction.followup.send(embed=embed)
        view = cls(data, title, description, message, interaction.user, inline, color)
        await message.edit(embed=view.pages[0] if view.pages else embed, view=view)
        return view

    def __init__(
        self,
        data,
        title,
        description,
        message: discord.Message,
        user: discord.User,
        inline=False,
        color: discord.Color = discord.Color.blue(),
    ):
        super().__init__(timeout=60)
        self.pages = list(
            PaginationView.chunk_data(data, 10, title, description, inline, color)
        )
        self.current_page = 0
        self.message = message
        self.user = user

        self.children[1].disabled = len(self.pages) <= 1

    @staticmethod
    def chunk_data(data, items_per_page, title, description, inline, color):
        for i in range(0, len(data), items_per_page):
            embed = discord.Embed(title=title, description=description, color=color)
            for x in data[i : i + items_per_page]:
                embed.add_field(name=x["name"], value=x["value"], inline=inline)
            yield embed

    async def update_message(self):
        """Updates the message with the current page content."""
        embed = self.pages[self.current_page]
        await self.message.edit(embed=embed, view=self)
    
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        await self.message.edit(view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Handles the Previous button click."""
        await interaction.response.defer()
        self.current_page -= 1
        if self.current_page == 0:
            button.disabled = True
        self.children[1].disabled = False  # Enable Next button
        await self.update_message()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        """Handles the Next button click."""
        try:
            await interaction.response.defer()
            self.current_page += 1
            if self.current_page == len(self.pages) - 1:
                button.disabled = True
            self.children[0].disabled = False  # Enable Previous button
            await self.update_message()
        except Exception as e:
            traceback.print_exc()
            await interaction.followup.send(
                "An error occurred while trying to paginate.", ephemeral=True
            )

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Handles the Stop button click."""
        await interaction.response.defer()
        if self.user.id != interaction.user.id:
            await interaction.followup.send(content="You are not the user using this!", ephemeral=True)
            return
        await self.message.edit(content="Pagination stopped.", embed=None, view=None)
        self.stop()
