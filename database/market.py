from .core import CoreDB


class MarketDB(CoreDB):
    async def get_market(self):
        return (await self.supabase.rpc("get_market_items").execute()).data

    async def sell_item_market(
        self, user_id: str, item_id: int, price: int, amount: int
    ) -> int:
        return (
            await self.supabase.rpc(
                "put_items_on_sale",
                {
                    "p_user_id": user_id,
                    "p_item_id": item_id,
                    "p_sell_price": price,
                    "n": amount,
                },
            ).execute()
        ).data

    async def delete_item_market(self, item_id: int):
        await self.supabase.table("market").delete().eq("id", item_id).execute()

    async def get_item_market(self, item_id: int):
        return (
            await self.supabase.table("market")
            .select("*, items (name)")
            .eq("id", item_id)
            .execute()
        ).data

    async def get_market_by_user_id(self, user_id: str):
        return (
            await self.supabase.rpc(
                "get_market_items_by_user", {"p_user_id": user_id}
            ).execute()
        ).data

    async def buy_market_item(self, user_id: str, item_id: int):
        return await self.supabase.rpc(
            "buy_market_item", {"p_user_id": user_id, "p_market_id": item_id}
        ).execute()
