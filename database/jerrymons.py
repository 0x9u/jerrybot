from .core import CoreDB


class JerrymonsDB(CoreDB):
    async def get_jerrymon_by_id(self, jerrymon_id: int) -> dict:
        return (await self.supabase.table("jerrymons").select("*").eq("id", jerrymon_id).execute()).data[0]

    async def get_jerrymon_inventory_count(self, user_id: str) -> int:
        return (await self.supabase.table("jerrymons_inventory").select("*", count="exact").eq("user_id", user_id).execute()).count

    async def get_jerrymon(self, jerrymon_name: str) -> dict:
        return (await self.supabase.table("jerrymons").select("*").eq("name", jerrymon_name).execute()).data

    async def get_jerrymon_party(self, user_id: str) -> list:
        return (await self.supabase.table("jerrymons_inventory").select("*, jerrymons(*)").eq("user_id", user_id).eq("in_party", True).execute()).data

    async def get_jerrymon_party_count(self, user_id: str) -> int:
        data = (await self.supabase.table("jerrymons_inventory").select("*", count="exact").eq("user_id", user_id).eq("in_party", True).execute()).count
        print(data, await self.get_jerrymon_party(user_id))
        return data if data is not None else 0

    async def get_jerrymon_box(self, user_id: str) -> list:
        # todo: do order by id
        return (await self.supabase.table("jerrymons_inventory").select("*, jerrymons(*)").eq("user_id", user_id).eq("in_party", False).execute()).data

    async def get_jerrymon_box_count(self, user_id: str) -> int:
        data = (await self.supabase.table("jerrymons_inventory").select("*", count="exact").eq("user_id", user_id).eq("in_party", False).execute()).count
        return data if data is not None else 0

    async def get_jerrymon_inventory_by_id(self, user_id: str, id: int):
        jerrymon = await self.supabase.table("jerrymons_inventory").select("*, jerrymons(*)").eq("user_id", user_id).eq("id", id).execute()
        return jerrymon.data[0] if len(jerrymon.data) > 0 else None

    async def get_jerrymon_inventory_by_nickname(self, user_id: str, nickname: str):
        jerrymon = await self.supabase.table("jerrymons_inventory").select("*").eq("user_id", user_id).eq("nickname", nickname).execute()
        return jerrymon.data[0] if len(jerrymon.data) > 0 else None
    
    async def get_jerrymon_known_moves(self, jerrymon_inventory_id: int):
        return (await self.supabase.table("jerrymons_known_moves").select("*, jerrymons_moves(*)").eq("jerrymon_inventory_id", jerrymon_inventory_id).execute()).data

    async def get_jerrymon_known_moves_count(self, jerrymon_inventory_id: int):
        return (await self.supabase.table("jerrymons_known_moves").select("*", count="exact").eq("jerrymon_inventory_id", jerrymon_inventory_id).execute()).count

    async def nickname_jerrymon(self, user_id: str, jerrymon_id: int, nickname: str):
        return await self.supabase.table("jerrymons_inventory").update({"nickname": nickname}).eq("user_id", user_id).eq("id", jerrymon_id).execute()

    async def remove_jerrymon_from_inventory(self, user_id: str, jerrymon_id: int):
        return await self.supabase.table("jerrymons_inventory").delete().eq("user_id", user_id).eq("id", jerrymon_id).execute()

    async def transfer_jerrymon_from_inventory(self, user_id: str, jerrymon_id: int, new_user_id: str):
        return await self.supabase.table("jerrymons_inventory").update({"user_id": new_user_id, "in_party": False}).eq("user_id", user_id).eq("id", jerrymon_id).execute()

    async def move_jerrymon_party(self, user_id: str, jerrymon_id: int, in_party: bool):
        return await self.supabase.table("jerrymons_inventory").update({"in_party": in_party}).eq("user_id", user_id).eq("id", jerrymon_id).execute()

    async def get_random_jerrymon(self):
        return (await self.supabase.rpc("get_random_jerrymon").execute()).data["id"]

    async def add_jerrymon_to_inventory(self, user_id: str, jerrymon_id: int) -> int:
        # adds default move to jerrymon too
        # returns id of newly created
        return (await self.supabase.rpc("add_jerrymon_to_inventory", {"p_user_id": user_id, "p_jerrymon_id": jerrymon_id}).execute()).data

    async def get_alive_jerrymons(self, user_id: str):  # probs not needed anymore
        return (await self.supabase.table("jerrymons_inventory").select("*").eq("user_id", user_id).gt("hp", 0).execute()).data

    async def get_jerrymon_move_tree_by_lvl(self, jerrymon_id: int, lvl: int) -> list[int]:
        result = await self.supabase.table("jerrymons_move_tree").select("jerrymon_move_id").eq("jerrymon_id", jerrymon_id).eq("level_earned", lvl).execute()

        # Extract the data safely and return a list of ints
        if result.data:
            return [row["jerrymon_move_id"] for row in result.data]
        return []

    async def save_jerrymon(self, jerrymon: dict):
        return await self.supabase.table("jerrymons_inventory").update(jerrymon).eq("id", jerrymon["id"]).execute()
