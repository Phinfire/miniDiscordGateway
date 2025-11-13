"""
FastAPI REST Server for Discord Guild User Retrieval
Wraps discord.py client with async HTTP endpoints
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .discord_client import DiscordClientManager
from .services import get_guild_users
from .models import GuildUsersResponse, ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Discord token from environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set")

# Discord client instance (singleton)
client = DiscordClientManager.get_client(DISCORD_TOKEN)

# Track client startup
client_ready = asyncio.Event()

@client.event
async def on_ready():
    """Called when Discord client is ready."""
    logger.info(f"✅ Discord bot ready as {client.user}")
    client_ready.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown of Discord client.
    """
    # Startup: Start the Discord client in a background task
    logger.info("🚀 Starting Discord client...")
    
    async def run_discord_client():
        try:
            await DiscordClientManager.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Discord client error: {e}")
    
    discord_task = asyncio.create_task(run_discord_client())
    
    # Wait for client to be ready (with timeout)
    try:
        await asyncio.wait_for(client_ready.wait(), timeout=10.0)
        logger.info("Discord client is ready")
    except asyncio.TimeoutError:
        logger.error("Discord client failed to initialize within timeout")
        discord_task.cancel()
        raise
    
    yield
    
    # Shutdown: Close Discord client
    logger.info("🛑 Shutting down Discord client...")
    await DiscordClientManager.close()
    discord_task.cancel()
    try:
        await discord_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app with lifespan
app = FastAPI(
    title="Mini Discord Gateway API",
    description="REST API to retrieve Discord guild users",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Check API and Discord client health."""
    return {
        "status": "ok",
        "discord_client_ready": client.is_ready(),
        "discord_bot_name": str(client.user) if client.user else "Not connected"
    }


@app.get(
    "/guild/{guild_id}/users",
    response_model=GuildUsersResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid guild ID"},
        404: {"model": ErrorResponse, "description": "Guild not found"},
        503: {"model": ErrorResponse, "description": "Discord client not ready"},
    },
    tags=["Guild Operations"]
)
async def get_guild_users_endpoint(guild_id: int) -> GuildUsersResponse:
    """
    Get all users in a Discord guild.
    
    Returns a JSON object mapping Discord user IDs → user info.
    
    **Example Response:**
    ```json
    {
        "guild_id": 987654321,
        "guild_name": "My Server",
        "total_members": 42,
        "users": {
            "123456789": {
                "id": 123456789,
                "username": "user",
                "discriminator": "0001",
                "display_name": "User Display Name",
                "avatar_url": "https://cdn.discordapp.com/...",
                "is_bot": false,
                "joined_at": "2023-01-15T10:30:00Z"
            }
        }
    }
    ```
    
    Args:
        guild_id: The Discord guild ID (snowflake format)
        
    Returns:
        GuildUsersResponse with user map
        
    Raises:
        HTTPException: If client not ready, guild not found, or invalid guild ID
    """
    
    # Validate guild_id
    if guild_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Guild ID must be a positive integer"
        )
    
    # Check if Discord client is ready
    if not client.is_ready():
        logger.error("Discord client is not ready")
        raise HTTPException(
            status_code=503,
            detail="Discord client is not ready. Please try again later."
        )
    
    try:
        # Fetch guild users using the service layer
        result = await get_guild_users(client, guild_id)
        return result
        
    except ValueError as e:
        logger.warning(f"Guild not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except discord.Forbidden:
        logger.error(f"Permission denied accessing guild {guild_id}")
        raise HTTPException(
            status_code=403,
            detail="Bot does not have permission to access this guild"
        )
        
    except discord.HTTPException as e:
        logger.error(f"Discord API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="Discord API error. Please try again later."
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@app.get("/", tags=["Info"])
async def root():
    """API information and status."""
    return {
        "name": "Mini Discord Gateway API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
