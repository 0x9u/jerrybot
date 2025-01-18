import os
from dotenv import load_dotenv
from supabase._async.client import create_client, AsyncClient as Client

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")


# CoreDB Class: Shared Supabase Client
class CoreDB:
    @classmethod
    async def create_db(cls):
        return cls(await create_client(SUPABASE_URL, SUPABASE_KEY))

    def __init__(self, client: Client):
        self.supabase: Client = client
        self.ratelimit: dict[str, int] = {}
