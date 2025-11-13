import discord
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DiscordClientManager:
    _instance: Optional[discord.Client] = None
    
    @classmethod
    def get_client(cls, token: str) -> discord.Client:
        """Get or create the Discord client (singleton pattern)."""
        if cls._instance is None:
            intents = discord.Intents.default()
            intents.members = True  # Required to list guild members
            intents.guilds = True
            
            cls._instance = discord.Client(intents=intents)
            
            @cls._instance.event
            async def on_ready():
                logger.info(f"Discord bot logged in as {cls._instance.user}")
        
        return cls._instance
    
    @classmethod
    async def start(cls, token: str):
        """Start the Discord client (blocking)."""
        client = cls.get_client(token)
        await client.start(token)
    
    @classmethod
    async def close(cls):
        """Close the Discord client."""
        if cls._instance and cls._instance.is_closed() is False:
            await cls._instance.close()
            cls._instance = None
