from .admin import AdminDB
from .buffs import BuffDB
from .coins import CoinsDB
from .demand import DemandDB
from .farm import FarmDB
from .inventory import InventoryDB
from .investing import InvestingDB
from .items import ItemDB
from .jobs import JobsDB
from .leaderboard import LeaderboardDB
from .market import MarketDB
from .tycoon import TycoonDB
from .user import UserDB
from .jerrymons import JerrymonsDB

class DB(
    AdminDB,
    BuffDB,
    CoinsDB,
    DemandDB,
    FarmDB,
    InventoryDB,
    InvestingDB,
    ItemDB,
    JobsDB,
    LeaderboardDB,
    MarketDB,
    TycoonDB,
    UserDB,
    JerrymonsDB
    
):
    pass

# Global instance baby

db :DB = None
async def initialise_db():
    global db
    db = await  DB.create_db()
    print(f"initialsied db {db}")



__all__ = ["db", "initialise_db"]
