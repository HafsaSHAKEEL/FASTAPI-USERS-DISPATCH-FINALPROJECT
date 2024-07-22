import logging

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

import models
import database
from routers import auth, dispatch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log database connection
logger.info("Connecting to the database")
logger.info(f"Database URL: {database.SQLALCHEMY_DATABASE_URL}")

# Log table creation
try:
    logger.info("Creating tables")
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Tables created successfully")
except Exception as e:
    logger.error(f"Error creating tables: {e}")

app.include_router(auth.router)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
app.include_router(dispatch.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

