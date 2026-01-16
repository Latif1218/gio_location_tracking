from fastapi import FastAPI, status
from .database import Base, engine
from .router import user, register_user, location, forgot      
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/health', status_code=status.HTTP_200_OK)
def health():
    return {"status": "OK"}

# User related routers
app.include_router(user.router)
app.include_router(register_user.router)

# Static files (map.html etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Location router
app.include_router(location.router)  # prefix is already /location

# forgot router
app.include_router(forgot.router)
