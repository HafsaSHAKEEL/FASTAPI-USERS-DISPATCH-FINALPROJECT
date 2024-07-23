from fastapi import FastAPI
import models
from database import engine
from routers import auth, dispatch

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dispatch.router, tags=["dispatch"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Dispatch API"}
