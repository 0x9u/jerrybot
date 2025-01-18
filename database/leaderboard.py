from .core import CoreDB


class LeaderboardDB(CoreDB):
    async def get_leaderboard(self):
        return (
            await self.supabase.table("leaderboard")
            .select("*")
            .order("count", desc=True)
            .limit(15)
            .execute()
        ).data

    async def get_leaderboard_highest(self):
        data = (
            await self.supabase.table("leaderboard")
            .select("*")
            .order("count", desc=True)
            .limit(1)
            .execute()
        ).data
        if len(data) > 0:
            return data[0]
        return None

    async def update_leaderboard(self, user_id: str, new_count: int):
        """
        Updates the leaderboard with a new entry for the given user.

        If the user already has an entry in the leaderboard, the count is incremented by one.
        If the user doesn't have an entry in the leaderboard, a new entry is created with a count of 1.

        Parameters
        ----------
        user_id : str
            The id of the user to update the leaderboard for
        new_count : int
            The number of new racial slurs to add to the leaderboard
        """

        countData = (
            await self.supabase.table("leaderboard")
            .select("count")
            .eq("user_id", user_id)
            .execute()
        )
        count = 0 if len(countData.data) == 0 else countData.data[0].get("count")
        await self.supabase.table("leaderboard").upsert(
            {"user_id": user_id, "count": count + new_count}
        ).execute()

    async def get_leaderboard_guild(self, guild_id: str) -> list:
        """
        Gets the leaderboard for the given guild.

        Parameters
        ----------
        guild_id : str
            The id of the guild to get the leaderboard for

        Returns
        -------
        list
            A list of dictionaries containing the leaderboard data for the given guild
        """
        return (
            await self.supabase.table("leaderboard_guild")
            .select("*")
            .eq("guild_id", guild_id)
            .limit(15)
            .order("count", desc=True)
            .execute()
        ).data

    async def update_leaderboard_guild(
        self, user_id: str, guild_id: str, new_count: int
    ):
        """
        Updates the leaderboard for the given guild with a new entry for the given user.

        If the user already has an entry in the leaderboard for the given guild, the count is incremented by one.
        If the user doesn't have an entry in the leaderboard for the given guild, a new entry is created with a count of 1.

        Parameters
        ----------
        user_id : str
            The id of the user to update the leaderboard for
        guild_id : str
            The id of the guild to update the leaderboard for
        new_count : int
            The new count to add to the leaderboard entry
        """
        countData = (
            await self.supabase.table("leaderboard_guild")
            .select("count")
            .eq("guild_id", guild_id)
            .eq("user_id", user_id)
            .execute()
        )
        count = 0 if len(countData.data) == 0 else countData.data[0].get("count")
        await self.supabase.table("leaderboard_guild").upsert(
            {"guild_id": guild_id, "user_id": user_id, "count": count + new_count}
        ).execute()

    async def get_user_word_count(self, user_id: str) -> int:
        return (
            (
                await self.supabase.table("leaderboard")
                .select("count")
                .eq("user_id", user_id)
                .execute()
            )
            .data[0]
            .get("count")
        )

    async def get_user_coins_leaderboard(self, bot_id: str) -> list:
        return (
            await self.supabase.table("users")
            .select("*")
            .not_.eq("id", bot_id)
            .order("coins", desc=True)
            .limit(15)
            .execute()
        ).data

    async def get_user_slaves_leaderboard(self) -> list:
        return (
            await self.supabase.table("users")
            .select("*")
            .order("slaves", desc=True)
            .limit(15)
            .execute()
        ).data
