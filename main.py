from fastapi import FastAPI
from contextlib import asynccontextmanager
from src import (basic_router, auth_router, librarian_router, create_tables, drop_tables)
from dotenv import load_dotenv
import uvicorn


load_dotenv()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # await drop_tables()
    await create_tables()
    yield
    print("Shutdown...")


app = FastAPI(lifespan=lifespan)
app.include_router(basic_router)
app.include_router(auth_router)
app.include_router(librarian_router)


if __name__ == "__main__":
    uvicorn.run(app)
