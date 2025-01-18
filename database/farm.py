from .core import CoreDB


class FarmDB(CoreDB):
    async def get_farm_crops(self, user_id: str):
        return (
            await self.supabase.table("farm")
            .select("*, items ( name )")
            .eq("user_id", user_id)
            .execute()
        ).data

    async def harvest_farm(self, user_id: str):
        return (
            await self.supabase.rpc("harvest_farm", {"p_user_id": user_id}).execute()
        ).data

    async def add_farm_crop(self, user_id: str, item_id: int, amount: int):
        return (
            await self.supabase.table("farm")
            .insert([{"user_id": user_id, "seed_id": item_id} for _ in range(amount)])
            .execute()
        ).data
