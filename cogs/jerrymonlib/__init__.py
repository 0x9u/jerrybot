from .battle import JerryMonBattle
from .pets import JerryMonPets


class Jerrymon(JerryMonBattle, JerryMonPets):
    pass

__all__ = ["Jerrymon"]
