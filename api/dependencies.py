"""FastAPI dependencies for Uni Pilot API."""

from sqlalchemy.orm import Session

from database.base import get_db

# Database dependency - use this in route handlers
# Example: async def my_route(db: Session = Depends(get_db)):
get_database = get_db

