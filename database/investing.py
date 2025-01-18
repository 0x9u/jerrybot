from .core import CoreDB


class InvestingDB(CoreDB):
    async def update_user_portfolio(
        self, user_id: str, symbol: str, shares: int
    ) -> None:
        """
        Updates the user's portfolio in the database.
        If the user does not own the symbol, it will add it. If shares reduce to 0 or below, it removes the symbol.

        Args:
            user_id (str): The ID of the user.
            symbol (str): The stock symbol being updated.
            shares (int): The number of shares to add or subtract (can be negative).
        """

        symbol_entry = (
            await self.supabase.table("portfolio")
            .select("*")
            .eq("user_id", user_id)
            .eq("symbol", symbol)
            .execute()
        ).data

        if symbol_entry:
            # Update existing symbol entry
            new_shares = symbol_entry[0]["shares"] + shares
            if new_shares > 0:
                await self.supabase.table("portfolio").update(
                    {"shares": new_shares}
                ).eq("id", symbol_entry[0]["id"]).execute()
            else:
                # Remove symbol if shares drop to 0 or less
                await self.supabase.table("portfolio").delete().eq(
                    "id", symbol_entry[0]["id"]
                ).execute()
        else:
            # Add new symbol if shares are positive
            if shares > 0:
                await self.supabase.table("portfolio").insert(
                    {"user_id": user_id, "symbol": symbol, "shares": shares}
                ).execute()

    async def get_user_portfolio_stock(self, user_id: str, symbol: str):
        return (
            await self.supabase.table("portfolio")
            .select("*")
            .eq("user_id", user_id)
            .eq("symbol", symbol)
            .execute()
        ).data

    async def get_user_portfolio(self, user_id: str):
        return (
            await self.supabase.table("portfolio")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        ).data
