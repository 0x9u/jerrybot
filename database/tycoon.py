from .core import CoreDB


class TycoonDB(CoreDB):
    async def update_slaves(self, user_id: str, amount: int):
        """
        Updates the number of slaves for the given user in the database.

        Parameters
        ----------
        user_id : str
            The id of the user to update the number of slaves for
        amount : int
            The new number of slaves for the user
        """
        slaves = await self.get_slaves(user_id)
        await self.supabase.table("users").upsert(
            {"id": user_id, "slaves": slaves + amount}
        ).execute()

    async def get_slaves(self, user_id: str) -> int:
        return (
            (
                await self.supabase.table("users")
                .select("slaves")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("slaves")
        )

    async def update_farms(self, user_id: str, amount: int):
        farms = await self.get_farms(user_id)
        await self.supabase.table("users").update({"farms": farms + amount}).eq(
            "id", user_id
        ).execute()

    async def get_farms(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("farms")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("farms")
        )

    async def update_mines(self, user_id: str, amount: int):
        mines = await self.get_mines(user_id)
        await self.supabase.table("users").update({"mines": mines + amount}).eq(
            "id", user_id
        ).execute()

    async def get_mines(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("mines")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("mines")
        )
