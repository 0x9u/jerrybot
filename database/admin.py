from .core import CoreDB


class AdminDB(CoreDB):
    async def add_allowed_channel(self, guild_id: str, channel_id: str):
        await self.supabase.table("allowed_channels").insert(
            {"guild_id": guild_id, "channel_id": channel_id}
        ).execute()

    async def remove_allowed_channel(self, guild_id: str, channel_id: str):
        await self.supabase.table("allowed_channels").delete().eq(
            "guild_id", guild_id
        ).eq("channel_id", channel_id).execute()

    async def get_allowed_channel(self, guild_id: str, channel_id: str):
        return (
            await self.supabase.table("allowed_channels")
            .select("*")
            .eq("guild_id", guild_id)
            .eq("channel_id", channel_id)
            .execute()
        ).data
