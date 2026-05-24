"""
Health check and utility endpoints.
"""

from app.db.base import engine


async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
