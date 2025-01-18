import random
from enum import Enum
import discord
import asyncio

import traceback
from shared import shared
from math import ceil

ALIAS = {
    "phone": "Iphone 9 million pro max",
    "gun": "Gun Crate",
    "seed": "Seed Packet",
    "weed": "Marijuana",
    "coacine": "Coca",
    "cofee": "Coffee",
    "tobaco": "Tobacco",
    "coco": "Cocoa",
    "tea": "Tea",
    "weed seed": "Marijuana Seed",
    "coacine seed": "Coca Seed",
    "cofee seed": "Coffee Seed",
    "tobaco seed": "Tobacco Seed",
    "coco seed": "Cocoa Seed",
    "tea seed": "Tea Seed",
    "ak": "ak 69",
    "mac": "mac 10",
    "glock": "Glock",
}


class ItemCode(Enum):
    SLAVE = 1
    GUN_CRATE = 2
    SEED_PACKET = 3
    IPHONE = 4
    SAFE = 5
    EMOJI_ANNHILATOR = 6
    AK_69 = 7
    MAC_10 = 8
    GLOCK = 9
    RPG = 10
    MINE = 11
    FARM = 12
    MARIJUANA_SEED = 13
    TOBACCO_SEED = 14
    COCOA_SEED = 15
    COCA_SEED = 16
    COFFEE_SEED = 18
    TEA_SEED = 19
    MARIJUANA = 20
    TOBACCO = 21
    COCOA = 22
    COCA = 23
    COFFEE = 24
    TEA = 25
    BEAR_TRAP = 26
    BODYGUARD = 27
    ORBITAL_CANNON = 28

    # Centrelink Leecher Items
    WELFARE_CHEQUE = 29
    OLD_COUPON_BOOKLET = 30
    TATTERED_BACKPACK = 31
    FREE_BUS_PASS = 32
    CENTRELINK_MUG = 33
    BUDGET_PLANNER = 34
    GOVERNMENT_PEN = 35
    FINANCIAL_GUIDEBOOK = 36
    GOLDEN_BENEFIT_CARD = 37
    DIAMOND_SAVINGS_TOKEN = 38

    # Maccas Worker Items
    GREASY_UNIFORM = 39
    FRYING_BASKET = 40
    HAPPY_MEAL_TOY = 41
    MACCAS_HAT = 42
    CUSTOM_NAME_BADGE = 43
    GOLDEN_FRIES_KEYCHAIN = 44
    BIG_MAC_RECIPE = 45
    LIMITED_EDITION_SAUCE_PACKET = 46
    EMPLOYEE_OF_THE_MONTH_PLAQUE = 47
    MACCAS_GOLDEN_ARCH_TROPHY = 48

    # Maccas Manager Items
    MANAGER_CLIPBOARD = 49
    SPECIAL_EDITION_EMPLOYEE_HANDBOOK = 50
    MANAGER_TIE = 51
    FRANCHISEE_WELCOME_KIT = 52
    SCHEDULING_SOFTWARE_ACCESS_CARD = 53
    SIGNED_CORPORATE_MEMO = 54
    EXCLUSIVE_TEAM_JACKET = 55
    SECRET_MENU_ITEM_BLUEPRINT = 56
    GOLDEN_MANAGER_PIN = 57
    MACCAS_LIMITED_EDITION_GOLD_PLATED_PLAQUE = 58

    # Mayor Items
    CITY_HALL_PEN = 59
    PUBLIC_SPEECH_MICROPHONE = 60
    CAMPAIGN_POSTER = 61
    COMMEMORATIVE_RIBBON = 62
    OFFICIAL_KEY_TO_THE_CITY = 63
    SIGNED_LEGISLATION = 64
    MAYORS_GAVEL = 65
    CITY_PLANNING_BLUEPRINT = 66
    DIAMOND_ENCRUSTED_CITY_BADGE = 67
    MAYORS_GOLDEN_MEDAL_OF_SERVICE = 68

    # Thief Items
    BLACK_BANDANA = 69
    LOCKPICK_SET = 70
    CLANDESTINE_NOTE = 71
    LIGHTWEIGHT_GLOVES = 72
    REPLICA_JEWEL = 73
    FORGED_ID_CARD = 74
    MASTER_SAFE_CRACKER_KIT = 75
    BLUEPRINT_TO_THE_VAULT = 76
    PRICELESS_STOLEN_PAINTING = 77
    THE_ULTIMATE_HEIST_TROPHY = 78

    # Police Items
    PATROL_BADGE = 79
    FLASHLIGHT = 80
    HANDCUFFS = 81
    POLICE_CAP = 82
    SQUAD_CAR_DIE_CAST_MODEL = 83
    POLICE_JOURNAL = 84
    TACTICAL_VEST = 85
    RIOT_SHIELD = 86
    GOLDEN_SHERIFFS_BADGE = 87
    MEDAL_OF_VALOR = 88


loot_table_guns = {
    ItemCode.EMOJI_ANNHILATOR: 5,
    ItemCode.AK_69: 25,
    ItemCode.RPG: 35,
    ItemCode.MAC_10: 75,
    ItemCode.GLOCK: 95,
}

# Common 85-100%
# Uncommon 65-85%
# Rare 45-65%
# Epic 15-45%
# Legendary 0-15%

loot_table_seeds = {
    ItemCode.MARIJUANA_SEED: 75,
    ItemCode.TOBACCO_SEED: 95,
    ItemCode.COCOA_SEED: 65,
    ItemCode.COCA_SEED: 20,
    ItemCode.COFFEE_SEED: 50,
    ItemCode.TEA_SEED: 35,
}

# Loot table for Centrelink Leecher
loot_table_centrelink_leecher = {
    ItemCode.WELFARE_CHEQUE: 85,
    ItemCode.OLD_COUPON_BOOKLET: 90,
    ItemCode.TATTERED_BACKPACK: 75,
    ItemCode.FREE_BUS_PASS: 70,
    ItemCode.CENTRELINK_MUG: 60,
    ItemCode.BUDGET_PLANNER: 50,
    ItemCode.GOVERNMENT_PEN: 35,
    ItemCode.FINANCIAL_GUIDEBOOK: 25,
    ItemCode.GOLDEN_BENEFIT_CARD: 10,
    ItemCode.DIAMOND_SAVINGS_TOKEN: 5,
}

# Loot table for Maccas Worker
loot_table_maccas_worker = {
    ItemCode.GREASY_UNIFORM: 85,
    ItemCode.FRYING_BASKET: 90,
    ItemCode.HAPPY_MEAL_TOY: 75,
    ItemCode.MACCAS_HAT: 70,
    ItemCode.CUSTOM_NAME_BADGE: 60,
    ItemCode.GOLDEN_FRIES_KEYCHAIN: 50,
    ItemCode.BIG_MAC_RECIPE: 35,
    ItemCode.LIMITED_EDITION_SAUCE_PACKET: 25,
    ItemCode.EMPLOYEE_OF_THE_MONTH_PLAQUE: 10,
    ItemCode.MACCAS_GOLDEN_ARCH_TROPHY: 5,
}

# Loot table for Maccas Manager
loot_table_maccas_manager = {
    ItemCode.MANAGER_CLIPBOARD: 85,
    ItemCode.SPECIAL_EDITION_EMPLOYEE_HANDBOOK: 90,
    ItemCode.MANAGER_TIE: 75,
    ItemCode.FRANCHISEE_WELCOME_KIT: 70,
    ItemCode.SCHEDULING_SOFTWARE_ACCESS_CARD: 60,
    ItemCode.SIGNED_CORPORATE_MEMO: 50,
    ItemCode.EXCLUSIVE_TEAM_JACKET: 35,
    ItemCode.SECRET_MENU_ITEM_BLUEPRINT: 25,
    ItemCode.GOLDEN_MANAGER_PIN: 10,
    ItemCode.MACCAS_LIMITED_EDITION_GOLD_PLATED_PLAQUE: 5,
}

# Loot table for Mayor
loot_table_mayor = {
    ItemCode.CITY_HALL_PEN: 85,
    ItemCode.PUBLIC_SPEECH_MICROPHONE: 90,
    ItemCode.CAMPAIGN_POSTER: 75,
    ItemCode.COMMEMORATIVE_RIBBON: 70,
    ItemCode.OFFICIAL_KEY_TO_THE_CITY: 60,
    ItemCode.SIGNED_LEGISLATION: 50,
    ItemCode.MAYORS_GAVEL: 35,
    ItemCode.CITY_PLANNING_BLUEPRINT: 25,
    ItemCode.DIAMOND_ENCRUSTED_CITY_BADGE: 10,
    ItemCode.MAYORS_GOLDEN_MEDAL_OF_SERVICE: 5,
}

# Loot table for Thief
loot_table_thief = {
    ItemCode.BLACK_BANDANA: 85,
    ItemCode.LOCKPICK_SET: 90,
    ItemCode.CLANDESTINE_NOTE: 75,
    ItemCode.LIGHTWEIGHT_GLOVES: 70,
    ItemCode.REPLICA_JEWEL: 60,
    ItemCode.FORGED_ID_CARD: 50,
    ItemCode.MASTER_SAFE_CRACKER_KIT: 35,
    ItemCode.BLUEPRINT_TO_THE_VAULT: 25,
    ItemCode.PRICELESS_STOLEN_PAINTING: 10,
    ItemCode.THE_ULTIMATE_HEIST_TROPHY: 5,
}

# Loot table for Police
loot_table_police = {
    ItemCode.PATROL_BADGE: 85,
    ItemCode.FLASHLIGHT: 90,
    ItemCode.HANDCUFFS: 75,
    ItemCode.POLICE_CAP: 70,
    ItemCode.SQUAD_CAR_DIE_CAST_MODEL: 60,
    ItemCode.POLICE_JOURNAL: 50,
    ItemCode.TACTICAL_VEST: 35,
    ItemCode.RIOT_SHIELD: 25,
    ItemCode.GOLDEN_SHERIFFS_BADGE: 10,
    ItemCode.MEDAL_OF_VALOR: 5,
}


class EffectCode(Enum):
    ROB = 1
    EQUIP_TYPE = 2
    SEED_CONVERSION = 3  # seed to item
    XP_MULTIPLIER = 4
    COINS_MULTIPLIER = 5
    SLAVES_MULTIPLIER = 6


class EquipType(Enum):
    GUN = 1
    ACCESSORY = 2


async def get_equip_type(item) -> EquipType | None:
    import database

    return await database.db.get_item_effect(item, EffectCode.EQUIP_TYPE.value)


async def get_loot(loot_table: dict[ItemCode, int]) -> str | None:
    random_number = random.randint(1, sum(loot_table.values()))
    cum_prob = 0.0
    for item, prob in loot_table.items():
        cum_prob += prob
        if random_number <= cum_prob:
            return item.value


async def seed_to_plants(seed_id: int) -> int:
    import database

    return (
        await database.db.get_item_effect(seed_id, EffectCode.SEED_CONVERSION.value)
        or -1
    )


async def use_plants(plant_id: int) -> None | tuple[int, int, int]:
    import database

    xp_multiplier = (
        await database.db.get_item_effect(plant_id, EffectCode.XP_MULTIPLIER.value) or 1
    )
    coins_multiplier = (
        await database.db.get_item_effect(plant_id, EffectCode.COINS_MULTIPLIER.value)
        or 1
    )
    slaves_multiplier = (
        await database.db.get_item_effect(plant_id, EffectCode.SLAVES_MULTIPLIER.value)
        or 1
    )

    if xp_multiplier == 1 and coins_multiplier == 1 and slaves_multiplier == 1:
        return None
    return xp_multiplier, coins_multiplier, slaves_multiplier


async def job_lootbox(job_id: int) -> int:
    lookup = {
        2: loot_table_centrelink_leecher,
        3: loot_table_maccas_worker,
        4: loot_table_maccas_manager,
        5: loot_table_mayor,
        6: loot_table_thief,
        7: loot_table_police,
    }
    return await get_loot(lookup[job_id])


ITEMS_PER_LEVEL_SLAVES_RATE = 150
BASE_ITEMS_PER_LEVEL_SLAVES = 1000
ITEMS_PER_LEVEL_FARMS_RATE = 25
BASE_ITEMS_PER_LEVEL_FARMS = 100
ITEMS_PER_LEVEL_MINES_RATE = 10
BASE_ITEMS_PER_LEVEL_MINES = 50

MAX_BODYGUARDS = 10


def item_level_allowed(base: int, rate: int, level: int) -> int:
    return base + rate * level


def item_level_required(base: int, rate: int, total: int) -> int:
    return ceil((total - base) / rate)


async def handle_item_use(
    user_id: str,
    item,
    amount: int,
    interaction: discord.Interaction,
    self: discord.Client,
) -> bool:
    import database

    code = item["item_id"]

    level = await database.db.get_user_level(user_id)
    item_details = await database.db.get_item_by_id(code)
    item_level = item_details["level_require"]
    item_name = item_details["name"]

    if item_level is not None and level < item_level:
        await interaction.followup.send(
            f"You need level {item_level} to use a {item_name.lower()}"
        )
        return False

    try:
        match code:
            case ItemCode.FARM.value:
                slaves = await database.db.get_slaves(user_id)
                if slaves < 100:
                    await interaction.followup.send(
                        "You need at least 100 slaves to use a farm"
                    )
                    return False
                # calculate level required for farm
                farm_amount = await database.db.get_farms(user_id)
                amount_allowed = item_level_allowed(
                    BASE_ITEMS_PER_LEVEL_FARMS,
                    ITEMS_PER_LEVEL_FARMS_RATE,
                    await database.db.get_user_level(user_id),
                )
                total = farm_amount + amount
                if total > amount_allowed:
                    level_required = item_level_required(
                        BASE_ITEMS_PER_LEVEL_FARMS, ITEMS_PER_LEVEL_FARMS_RATE, total
                    )
                    await interaction.followup.send(
                        f"You need level {level_required} to have {total} farms"
                    )
                    return False
                await database.db.update_farms(user_id, amount)
            case ItemCode.MINE.value:
                slaves = await database.db.get_slaves(user_id)
                if slaves < 150:
                    await interaction.followup.send(
                        "You need at least 150 slaves to use a mine"
                    )
                    return False
                mine_amount = await database.db.get_mines(user_id)
                amount_allowed = item_level_allowed(
                    BASE_ITEMS_PER_LEVEL_MINES,
                    ITEMS_PER_LEVEL_MINES_RATE,
                    await database.db.get_user_level(user_id),
                )
                total = mine_amount + amount
                if total > amount_allowed:
                    level_required = item_level_required(
                        BASE_ITEMS_PER_LEVEL_MINES, ITEMS_PER_LEVEL_MINES_RATE, total
                    )
                    await interaction.followup.send(
                        f"You need level {level_required} to have {total} mines"
                    )
                    return False
                await database.db.update_mines(user_id, amount)
            case ItemCode.SLAVE.value:
                slave_amount = await database.db.get_slaves(user_id)
                amount_allowed = item_level_allowed(
                    BASE_ITEMS_PER_LEVEL_SLAVES,
                    ITEMS_PER_LEVEL_SLAVES_RATE,
                    await database.db.get_user_level(user_id),
                )
                total = slave_amount + amount
                if total > amount_allowed:
                    level_required = item_level_required(
                        BASE_ITEMS_PER_LEVEL_SLAVES, ITEMS_PER_LEVEL_SLAVES_RATE, total
                    )
                    await interaction.followup.send(
                        f"You need level {level_required} to have {total} slaves"
                    )
                    return False
                await database.db.update_slaves(user_id, amount)
            case ItemCode.GUN_CRATE.value:
                if amount > 20:
                    await interaction.followup.send(
                        "You can only open 20 crates at a time"
                    )
                    return False
                guns = await asyncio.gather(
                    *[get_loot(loot_table_guns) for _ in range(amount)]
                )
                for gun in guns:
                    await database.db.add_item_to_inventory(user_id, gun, 1)
            case ItemCode.IPHONE.value:
                if amount != 1:
                    await interaction.followup.send(
                        "You can only use 1 phone at a time"
                    )
                    return False
                if user_id in shared.heists:
                    shared.heists.remove(user_id)
                    await interaction.followup.send(
                        "You called the cops and they stopped the heist."
                    )
                else:
                    await interaction.followup.send(
                        "You tried to call the cops but realised that there was no heist going on."
                    )
            case ItemCode.SAFE.value:
                await database.db.update_max_bank_coins(user_id, 50 * amount)
            case ItemCode.SEED_PACKET.value:
                if amount > 20:
                    await interaction.followup.send(
                        "You can only open 20 seed packets at a time"
                    )
                    return False
                seeds = await asyncio.gather(
                    *[get_loot(loot_table_seeds) for _ in range(amount)]
                )
                for seed in seeds:
                    await database.db.add_item_to_inventory(user_id, seed, 1)
            case code if await seed_to_plants(code) != -1:
                await database.db.add_farm_crop(user_id, code, amount)
            case code if (multiplier := await use_plants(code)) is not None:
                if amount > 1:
                    await interaction.followup.send(
                        "You can only use 1 plant at a time"
                    )
                    return False
                await database.db.add_buff(user_id, *multiplier)
            case ItemCode.BEAR_TRAP.value:
                if amount > 1:
                    await interaction.followup.send(
                        "You can only use 1 bear trap at a time"
                    )
                    return False
                if await database.db.get_protection(user_id):
                    await interaction.followup.send(
                        "You can't use this while protected"
                    )
                    return False
                await database.db.update_protection(user_id, True)
            case ItemCode.BODYGUARD.value:
                current_bodyguards = await database.db.get_bodyguards(user_id)
                if current_bodyguards + amount > MAX_BODYGUARDS:
                    await interaction.followup.send(
                        f"You can only have {MAX_BODYGUARDS} bodyguards"
                    )
                    return False

                await database.db.update_bodyguards(user_id, amount)
            case ItemCode.ORBITAL_CANNON.value:
                # wait for user input to confirm
                await interaction.followup.send(
                    "Ping or type their user id to nuke them, or type `cancel` to cancel."
                )
                try:
                    message = await self.wait_for(
                        "message",
                        timeout=30,
                        check=lambda m: m.author == interaction.user,
                    )
                except asyncio.TimeoutError:
                    await interaction.followup.send("You took too long to respond.")
                    return False

                target_id = message.content
                if target_id.lower() == "cancel":
                    await interaction.followup.send("Nuke cancelled.")
                    return False

                if target_id.isdigit():
                    target_id = int(target_id)
                else:
                    # check if mention
                    message_mentions = message.mentions
                    if len(message_mentions) == 1:
                        target_id = message_mentions[0].id
                    else:
                        await interaction.followup.send(
                            "You must ping or type the user id of the person you want to nuke."
                        )
                        return False

                if target_id == user_id:
                    await interaction.followup.send("You can't nuke yourself.")
                    return False

                await database.db.delete_user(target_id)
                await interaction.followup.send("Nuke complete.")

                return False
            case _:
                print("NO MATCH")
                await interaction.followup.send(f"You can't use that.")
                return False
        return True
    except Exception as e:
        traceback.print_exc()


class IntOrAll:
    def __init__(self, value: str):
        if value.isdigit():
            self.value = int(value)
        elif value.lower() == "all":
            self.value = "all"
        else:
            raise ValueError("Input must be an integer or 'all'.")

    def __str__(self):
        return str(self.value)
