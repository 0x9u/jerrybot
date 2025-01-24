import enum

class JerrymonType(enum.Enum):
    Physical = 1
    Gun = 2
    Carrot = 3
    Rabbit = 4

class JerrymonStatusMove(enum.Enum):
    Poison = 1
    Heal = 2
    Stun = 3
    Speed = 4
    Attack = 5
    Defense = 6

class JerrymonStatusCondition(enum.Enum):
    Poison = 1
    Stun = 2

class JerrymonMoveCategory(enum.Enum):
    Attack = 1
    Special = 2
    Status = 3

JERRYMON_XP_GROWTH_RATE = 1.2
JERRYMON_BASE_XP = 100

def get_jerrymon_type(jerrymon_type: int) -> str | None:
    return JerrymonType(jerrymon_type).name if jerrymon_type in JerrymonType._value2member_map_ else None

def get_jerrymon_status_move(jerrymon_status_move: int) -> str | None:
    return JerrymonStatusMove(jerrymon_status_move).name if jerrymon_status_move in JerrymonStatusMove._value2member_map_ else None

def get_jerrymon_status_condition(jerrymon_status_condition: int) -> str | None:
    return JerrymonStatusCondition(jerrymon_status_condition).name if jerrymon_status_condition in JerrymonStatusCondition._value2member_map_ else None

def get_jerrymon_move_category(jerrymon_move_category: int) -> str | None:
    return JerrymonMoveCategory(jerrymon_move_category).name if jerrymon_move_category in JerrymonMoveCategory._value2member_map_ else None

def calculate_jerrymon_max_xp(jerrymon_level: int) -> int:
    return JERRYMON_BASE_XP * (JERRYMON_XP_GROWTH_RATE ** (jerrymon_level - 1))

def jerrymon_calculate_damage(jerrymon_attack: int, move_power: int,  opponent_defense: int) -> int:
    damage = ((2 * jerrymon_attack * move_power / opponent_defense) / 50) + 2
    return int(damage)
