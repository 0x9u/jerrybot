from .core import CoreDB


class ItemDB(CoreDB):
    async def get_items_shop(self):
        """
        Retrieves all items from the items table in the database that have a non-null price.

        Returns
        -------
        list
            A list of dictionaries containing the data for items with a non-null price.
        """
        return (
            await self.supabase.table("items").select("*").order("price").eq("in_shop", True).execute()
        ).data

    async def get_all_items(self):
        """
        Retrieves all items from the items table in the database.

        Returns
        -------
        list
            A list of dictionaries containing the data for all items.
        """
        return (await self.supabase.table("items").select("*").execute()).data

    async def get_item_shop(self, name: str):
        """
        Retrieves the item from the items table in the database with the given name that has a non-null price.

        Parameters
        ----------
        name : str
            The name of the item to retrieve

        Returns
        -------
        dict
            A dictionary containing the data for the item with the given name and a non-null price
        """
        return (
            await self.supabase.table("items")
            .select("*")
            .eq("in_shop", True)
            .eq("name", name)
            .execute()
        ).data

    async def get_item(self, name: str):
        """
        Retrieves the item from the items table in the database with the given name.

        Parameters
        ----------
        name : str
            The name of the item to retrieve

        Returns
        -------
        dict
            A dictionary containing the data for the item with the given name
        """
        return (
            await self.supabase.table("items").select("*").eq("name", name).execute()
        ).data

    async def get_item_by_id(self, id: int):
        return (
            await self.supabase.table("items").select("*").eq("id", id).execute()
        ).data[0]
