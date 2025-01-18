from .core import CoreDB
from datetime import datetime


class InventoryDB(CoreDB):
    async def get_inventory(self, user_id: str):
        """
        Retrieves the inventory for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the inventory for

        Returns
        -------
        list
            A list of dictionaries containing the inventory data for the given user
        """
        return (
            await self.supabase.table("inventory_count")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        ).data

    async def add_item_to_inventory(self, user_id: str, item_id: int, amount: int):
        """
        Adds the given item to the inventory of the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to add the item to
        item_id : int
            The id of the item to add
        """
        await self.supabase.rpc(
            "bulk_insert_inventory",
            {"p_user_id": user_id, "p_item_id": item_id, "p_amount": amount},
        ).execute()

    async def remove_item_from_inventory(self, user_id: str, item_id: int, amount: int):
        """
        Removes the given item from the inventory of the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to remove the item from
        item_id : int
            The id of the item to remove
        """

        await self.supabase.rpc(
            "delete_item_inventory",
            {"p_user_id": user_id, "p_item_id": item_id, "n": amount},
        ).execute()

    async def get_item_inventory_count(self, user_id: str, item_name: str):
        return (
            await self.supabase.table("inventory_count")
            .select("*")
            .eq("user_id", user_id)
            .filter("name", "eq", item_name)
            .execute()
        ).data

    async def get_item_inventory_count_id(self, user_id: str, item_id: str):
        return (
            await self.supabase.table("inventory_count")
            .select("*")
            .eq("user_id", user_id)
            .filter("item_id", "eq", item_id)
            .execute()
        ).data

    async def transfer_item_inventory(
        self, user_id: str, other_user_id: str, item_id: int, amount: int
    ):
        await self.supabase.rpc(
            "transfer_item",
            {
                "p_user_id": user_id,
                "p_other_user_id": other_user_id,
                "p_item_id": item_id,
                "n": amount,
            },
        ).execute()

    async def use_item_inventory(self, user_id: str, item_id: int, amount: int):
        await self.supabase.rpc(
            "use_item_inventory",
            {"p_user_id": user_id, "p_item_id": item_id, "p_amount": amount},
        ).execute()

    async def get_item_inventory_by_id(self, user_id: str, item_id: int):
        return (
            await self.supabase.table("inventory")
            .select("*")
            .eq("user_id", user_id)
            .eq("item_id", item_id)
            .execute()
        ).data

    async def get_item_inventory_by_name(self, user_id: str, item_name: str):

        return (
            await self.supabase.table("inventory")
            .select("*, items!inner( name )")
            .eq("user_id", user_id)
            .eq("items.name", item_name)
            .execute()
        ).data

    async def update_item_inventory(
        self, user_id: str, inventory_id: int, uses_left: int
    ):
        """
        Updates the inventory for a given item of the user with the new number of uses left.

        Parameters
        ----------
        user_id : str
            The id of the user whose inventory is to be updated
        inventory_id : int
            The id of the inventory entry to be updated
        uses_left : int
            The updated number of uses left for the item
        """
        await self.supabase.table("inventory").update(
            {"user_id": user_id, "id": inventory_id, "uses_left": uses_left}
        ).execute()

    async def equip_gun(self, user_id: str, item_id: int):
        await self.supabase.table("equip").upsert(
            {"user_id": user_id, "gun_id": item_id}
        ).execute()

    async def unequip_gun(self, user_id: str):
        await self.supabase.table("equip").upsert(
            {"user_id": user_id, "gun_id": None}
        ).execute()

    async def equip_accessory(self, user_id: str, item_id: int):
        await self.supabase.table("equip").upsert(
            {"user_id": user_id, "accessory_id": item_id}
        ).execute()

    async def unequip_accessory(self, user_id: str):
        await self.supabase.table("equip").upsert(
            {"user_id": user_id, "accessory_id": None}
        ).execute()

    async def get_equipped(self, user_id: str):
        """
        Retrieves the equipped items for the given user.

        Parameters
        ----------
        user_id : str
            The id of the user to get the equipped items for

        Returns
        -------
        list
            A list of dictionaries containing the equipped items data for the given user
        """
        # check
        data = (
            await self.supabase.table("equip")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        ).data
        if len(data) == 0:
            await self.supabase.table("equip").insert({"user_id": user_id}).execute()
            return (
                await self.supabase.table("equip")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            ).data[0]
        return data[0]

    async def get_item_effect(self, item_id: int, effect_type: int):
        """
        Retrieves the effect value for a given item and effect type.

        Parameters
        ----------
        item_id : int
            The id of the item to get the effect for
        effect_type : int
            The type of effect to get

        Returns
        -------
        int
            The effect value for the given item and effect type
        """
        data = (
            await self.supabase.table("effects")
            .select("value")
            .eq("item_id", item_id)
            .eq("effect_type", effect_type)
            .execute()
        ).data
        if not data:
            return None
        return data[0].get("value")

    async def update_item_demand(self, item_id: int, amount: int):
        data = (
            await self.supabase.table("demand")
            .select("demand_count, id")
            .eq("item_id", item_id)
            .eq("purchase_date", datetime.now().date())
            .execute()
        ).data
        if len(data) == 0:
            await self.supabase.table("demand").insert(
                {"item_id": item_id, "demand_count": amount}
            ).execute()
            return
        current = data[0].get("demand_count")
        id = data[0].get("id")
        await self.supabase.table("demand").update(
            {"item_id": item_id, "demand_count": current + amount}
        ).eq("id", id).execute()
