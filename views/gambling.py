import discord
import numpy as np
import asyncio

class BlackJackView(discord.ui.View):
    def __init__(self, user_id : int, message : discord.Message, embed : discord.Embed):
          super().__init__(timeout=120)
          self.user_id = user_id
          self.message = message
          self.embed = embed
          self.card_display_user : list[str] = []

          self.card_display_dealer : list[str] = []

          self.won : bool | None = None
          self.tie : bool = False

          self.double_down : bool = False
    
    async def deal_initial_cards(self):
        self.card_display_user.append(self.display_card(np.random.randint(1, 11)))
        self.card_display_user.append(self.display_card(np.random.randint(1, 11)))

        self.card_display_dealer.append(self.display_card(np.random.randint(1, 11)))
        self.card_display_dealer.append(self.display_card(np.random.randint(1, 11)))

        self.embed.set_field_at(0, name="Your Deck", value=f"Cards: {', '.join(self.card_display_user)}", inline=False)
        self.embed.set_field_at(1, name="Dealer Deck", value=f"Cards: {', '.join(self.card_display_dealer)}", inline=False)

        await self.message.edit(embed=self.embed, view=self)

        if self.count_total(self.card_display_user) == 21 and self.count_total(self.card_display_dealer) == 21:
            self.stop()
            self.tie = True
            return
        elif self.count_total(self.card_display_user) == 21:
            self.stop()
            self.won = True
            return
        elif self.count_total(self.card_display_dealer) == 21:
            self.stop()
            self.won = False
            return


    def display_card(self, card: int) -> str:
        if card == 10:
            # display as J, Q, K
            return np.random.choice(["J", "Q", "K"])
        elif card == 1:
            return "A"
        else:
            return str(card)
      
    def count_total(self, cards: list[str]) -> int:
        total = 0
        ace_count = 0
        for card in cards:
            if card in ["J", "Q", "K"]:
                total += 10
            elif card == "A":
                total += 11
                ace_count += 1
            else:
                total += int(card)
        
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total
    
    async def dealer_turn(self):
        card = np.random.randint(1, 11)
        self.card_display_dealer.append(self.display_card(card))

        self.embed.set_field_at(0, name="Your Deck", value=f"Cards: {', '.join(self.card_display_user)}", inline=False)
        self.embed.set_field_at(1, name="Dealer Deck", value=f"Cards: {', '.join(self.card_display_dealer)}", inline=False)

        if self.count_total(self.card_display_dealer) > 21:
            self.stop()
            self.won = True
            return
        elif self.count_total(self.card_display_dealer) == 21:
            self.stop()
            self.won = False
            return

        await self.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):   
        await interaction.response.defer()

        if self.user_id != interaction.user.id:
            await interaction.response.send_message("Only the user who started this game can hit!", ephemeral=True)
            return

        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.label == "Double Down":
                item.disabled = True

        card = np.random.randint(1, 11)
        self.card_display_user.append(self.display_card(card))
        

        self.embed.set_field_at(0, name="Your Deck", value=f"Cards: {', '.join(self.card_display_user)}", inline=False)
        self.embed.set_field_at(1, name="Dealer Deck", value=f"Cards: {', '.join(self.card_display_dealer)}", inline=False)

        # add card to message
        await self.message.edit(embed=self.embed, view=self)

        if self.count_total(self.card_display_user) > 21:
            self.stop()
            self.won = False
            return
        elif self.count_total(self.card_display_user) == 21:
            self.stop()
            self.won = True
            return

        await self.dealer_turn()
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if self.user_id != interaction.user.id:
            await interaction.response.send_message("Only the user who started this game can stand!", ephemeral=True)
            return
        
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.label == "Double Down":
                item.disabled = True
        
        await self.dealer_turn()
        
    @discord.ui.button(label="Double Down", style=discord.ButtonStyle.blurple)
    async def double_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        if self.user_id != interaction.user.id:
            await interaction.response.send_message("Only the user who started this game can double down!", ephemeral=True)
            return

        self.double_down = True

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        self.card_display_user.append(self.display_card(np.random.randint(1, 11)))
        
        self.embed.set_field_at(0, name="Your Deck", value=f"Cards: {', '.join(self.card_display_user)}", inline=False)
        self.embed.set_field_at(1, name="Dealer Deck", value=f"Cards: {', '.join(self.card_display_dealer)}", inline=False)
        
        await self.message.edit(embed=self.embed, view=self)

        if self.count_total(self.card_display_user) > 21:
            self.stop()
            self.won = False
            return
        elif self.count_total(self.card_display_user) == 21:
            self.stop()
            self.won = True
            return

        while self.won is None:
          await asyncio.sleep(1)
          await self.dealer_turn()
