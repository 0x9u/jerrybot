from .core import CoreDB
from utils import can_level_up


class UserDB(CoreDB):
    async def delete_user(self, user_id: str):
        await self.supabase.table("users").delete().eq("id", user_id).execute()

    async def verify_user(self, user_id: str) -> bool:
        """
        Verifies that a user exists in the database, adding them if they don't.

        Parameters
        ----------
        user_id : str
            The id of the user to verify

        Returns
        -------
        bool
            True if the user existed in the database, False if they didn't
        """
        # add user to the database if they don't exist
        user = (
            await self.supabase.table("users").select("*").eq("id", user_id).execute()
        )
        if len(user.data) == 0:
            await self.supabase.table("users").insert({"id": user_id}).execute()
            return False
        return True

    async def get_user_ratelimit(self, user_id: str) -> int:
        """
        Gets the ratelimit for the given user.

        This function caches the result to avoid repeated database queries.

        Parameters
        ----------
        user_id : str
            The id of the user to get the ratelimit for

        Returns
        -------
        int
            The ratelimit for the given user
        """

        if user_id in self.ratelimit:
            return self.ratelimit[user_id]

        self.ratelimit[user_id] = (
            (
                await self.supabase.table("users")
                .select("ratelimit")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("ratelimit")
        )
        return self.ratelimit[user_id]

    async def invalidate_user_ratelimit(self, user_id: str):
        """
        Invalidates the cached ratelimit for the given user.

        This function removes the user's ratelimit from the cache,
        forcing the next retrieval to query the database.

        Parameters
        ----------
        user_id : str
            The id of the user whose ratelimit cache is to be invalidated
        """
        del self.ratelimit[user_id]

    async def update_user_ratelimit(self, user_id: str, ratelimit: int):
        """
        Updates the ratelimit for the given user in the database and caches the result.

        Parameters
        ----------
        user_id : str
            The id of the user to update the ratelimit for
        ratelimit : int
            The new ratelimit for the user
        """
        await self.supabase.table("users").upsert(
            {"id": user_id, "ratelimit": ratelimit}
        ).execute()
        self.ratelimit[user_id] = ratelimit

    async def get_user_level(self, user_id: str) -> int:
        """
        Gets the level for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the level for

        Returns
        -------
        int
            The level for the given user
        """
        levelData = (
            await self.supabase.table("users")
            .select("level")
            .eq("id", user_id)
            .execute()
        )
        level = levelData.data[0].get("level")
        return level

    async def update_user_xp(self, user_id: str, amount: int) -> bool:
        """
        Updates the XP for the given user in the database and checks if they leveled up.

        If the user leveled up, the user's level is incremented and the user's XP is reset to 0.

        Parameters
        ----------
        user_id : str
            The id of the user to update the XP for
        amount : int
            The amount of XP to add to the user

        Returns
        -------
        bool
            True if the user leveled up, False if they didn't
        """

        xp_data = (
            await self.supabase.table("users").select("xp").eq("id", user_id).execute()
        )
        xp = xp_data.data[0].get("xp")
        await self.supabase.table("users").upsert(
            {"id": user_id, "xp": xp + amount}
        ).execute()

        # check if leveled up
        level = await self.get_user_level(user_id)
        able_to_level_up = can_level_up(xp + amount, level)
        if able_to_level_up:
            await self.supabase.table("users").upsert(
                {"id": user_id, "level": level + 1}
            ).execute()
            await self.supabase.table("users").upsert(
                {"id": user_id, "xp": 0}
            ).execute()
        return able_to_level_up

    async def get_user_xp(self, user_id: str) -> int:
        """
        Gets the current XP for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the XP for

        Returns
        -------
        int
            The current XP for the given user
        """

        xp_data = (
            await self.supabase.table("users").select("xp").eq("id", user_id).execute()
        )
        return xp_data.data[0].get("xp")

    async def update_protection(self, user_id: str, protection: bool):
        return (
            await self.supabase.table("users")
            .update({"protected": protection})
            .eq("id", user_id)
            .execute()
        )

    async def get_protection(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("protected")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("protected")
        )

    async def get_bodyguards(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("bodyguards")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("bodyguards")
        )

    async def update_bodyguards(self, user_id: str, amount: int):
        current_amount = await self.get_bodyguards(user_id)
        return await (
            self.supabase.table("users")
            .update({"bodyguards": amount + current_amount})
            .eq("id", user_id)
            .execute()
        )
