from contextlib import asynccontextmanager
from fastapi import FastAPI
from Database.db import init_schema
from Routers.chatRouter import router as chatRouter
from Routers.PreTargetRouter import router as PreTargetRouter
from Routers.OptionRouter import router as OptionRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
    yield


app = FastAPI(title="RagTool", version="v1", lifespan=lifespan)
app.include_router(chatRouter, tags=["ChatBot"])
app.include_router(PreTargetRouter, tags=["PreTarget"])
app.include_router(OptionRouter, tags=["Options"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
