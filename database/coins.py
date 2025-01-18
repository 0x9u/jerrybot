from .core import CoreDB


class CoinsDB(CoreDB):
    async def get_user_coins(self, user_id: str) -> int:
        coins_data = (
            await self.supabase.table("users")
            .select("coins")
            .eq("id", user_id)
            .execute()
        )
        return coins_data.data[0].get("coins")

    async def update_user_coins(self, user_id: str, amount: int):
        """
        Updates the coins for the given user in the database.

        Parameters
        ----------
        user_id : str
            The id of the user to update the coins for
        coins : int
            The new coins for the user
        """
        coins_data = (
            await self.supabase.table("users")
            .select("coins")
            .eq("id", user_id)
            .execute()
        )
        coins = coins_data.data[0].get("coins")
        await self.supabase.table("users").upsert(
            {"id": user_id, "coins": coins + amount}
        ).execute()

    async def get_user_coins(self, user_id: str) -> int:
        """
        Gets the coins for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the coins for

        Returns
        -------
        int
            The coins for the given user
        """
        coins_data = (
            await self.supabase.table("users")
            .select("coins")
            .eq("id", user_id)
            .execute()
        )
        coins = coins_data.data[0].get("coins")
        return coins

    async def get_bank_coins(self, user_id: str) -> int:
        """
        Gets the bank coins for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the bank coins for

        Returns
        -------
        int
            The bank coins for the given user
        """
        coins_data = await (
            self.supabase.table("users")
            .select("banked_coins")
            .eq("id", user_id)
            .execute()
        )
        return coins_data.data[0].get("banked_coins")

    async def update_bank_coins(self, user_id: str, amount: int):
        """
        Updates the bank coins for the given user in the database.

        Parameters
        ----------
        user_id : str
            The id of the user to update the bank coins for
        amount : int
            The new bank coins for the user
        """
        coins_data = await (
            self.supabase.table("users")
            .select("banked_coins")
            .eq("id", user_id)
            .execute()
        )
        coins = coins_data.data[0].get("banked_coins")
        await self.supabase.table("users").upsert(
            {"id": user_id, "banked_coins": coins + amount}
        ).execute()

    async def get_max_bank_coins(self, user_id: str) -> int:
        """
        Gets the max bank coins for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the max bank coins for

        Returns
        -------
        int
            The max bank coins for the given user
        """
        coins_data = await (
            self.supabase.table("users")
            .select("max_banked_coins")
            .eq("id", user_id)
            .execute()
        )
        return coins_data.data[0].get("max_banked_coins")

    async def update_max_bank_coins(self, user_id: str, amount: int):
        """
        Updates the max bank coins for the given user in the database.

        Parameters
        ----------
        user_id : str
            The id of the user to update the max bank coins for
        amount : int
            The new max bank coins for the user
        """
        coins_data = await (
            self.supabase.table("users")
            .select("max_banked_coins")
            .eq("id", user_id)
            .execute()
        )
        coins = coins_data.data[0].get("max_banked_coins")
        await self.supabase.table("users").upsert(
            {"id": user_id, "max_banked_coins": coins + amount}
        ).execute()
