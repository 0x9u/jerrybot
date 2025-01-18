from .core import CoreDB

from datetime import datetime, timezone


class BuffDB(CoreDB):
    async def add_buff(
        self,
        user_id: str,
        xp_multiplier: int,
        coins_multiplier: int,
        slaves_multiplier: int,
    ):
        return (
            await self.supabase.table("buffs")
            .upsert(
                {
                    "user_id": user_id,
                    "xp_multiplier": xp_multiplier,
                    "coins_multiplier": coins_multiplier,
                    "slaves_multiplier": slaves_multiplier,
                    "time_created": datetime.now(timezone.utc).isoformat(),
                }
            )
            .execute()
        ).data

    async def get_buff(self, user_id: str):
        return (
            await self.supabase.table("buffs")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        ).data

    async def delete_buff(self, user_id: str):
        return await self.supabase.table("buffs").delete().eq("user_id", user_id).execute()
