from .core import CoreDB

from datetime import datetime


class JobsDB(CoreDB):
    async def get_jobs_list(self):
        return (
            await self.supabase.table("jobs").select("*").order("rate").execute()
        ).data

    async def get_current_job(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("job_id")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("job_id")
        )

    async def set_current_job(self, user_id: str, job_id: int):
        return (
            await self.supabase.table("users")
            .update({"job_id": job_id})
            .eq("id", user_id)
            .execute()
        )

    async def get_job(self, name: str):
        return (
            await self.supabase.table("jobs").select("*").eq("name", name).execute()
        ).data

    async def get_job_by_id(self, job_id: int):
        return (
            await self.supabase.table("jobs").select("*").eq("id", job_id).execute()
        ).data

    async def get_last_worked(self, user_id: str):
        return (
            (
                await self.supabase.table("users")
                .select("last_worked")
                .eq("id", user_id)
                .execute()
            )
            .data[0]
            .get("last_worked")
        )

    async def update_last_worked(self, user_id: str, last_worked: datetime):
        return (
            await self.supabase.table("users")
            .update({"last_worked": last_worked.isoformat()})
            .eq("id", user_id)
            .execute()
        )
