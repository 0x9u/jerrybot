from .jerrymonlib import Jerrymon

async def setup(bot):
    await bot.add_cog(Jerrymon(bot))
