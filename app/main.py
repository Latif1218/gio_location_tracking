from fastapi import FastAPI, status
from .database import Base, engine, get_db
from .router import user, register_user


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/health', status_code= status.HTTP_200_OK)
def health():
    return {"status": "OK"}


app.include_router(user.router)
app.include_router(register_user.router)