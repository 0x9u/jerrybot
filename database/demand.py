from .core import CoreDB


class DemandDB(CoreDB):
    async def get_current_demand(self, item_id: int):
        data = (
            await self.supabase.table("demand_last_30_days")
            .select("average")
            .eq("item_id", item_id)
            .execute()
        ).data
        if len(data) == 0:
            return 0
        return data[0].get("average")

    async def get_baseline_demand(self, item_id: int):
        data = await (
            self.supabase.table("demand_last_90_days")
            .select("average")
            .eq("item_id", item_id)
            .execute()
        )
        if len(data.data) == 0:
            return 0
        return data.data[0].get("average")
