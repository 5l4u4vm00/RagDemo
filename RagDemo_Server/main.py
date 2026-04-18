import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.db import init_schema
from Routers.chatRouter import router as chatRouter
from Routers.PreTargetRouter import router as PreTargetRouter
from Routers.OptionRouter import router as OptionRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
    yield


app = FastAPI(title="RagTool", version="v1", lifespan=lifespan)

_origins_env = os.environ.get(
    "CORS_ALLOW_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
allow_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatRouter, tags=["ChatBot"])
app.include_router(PreTargetRouter, tags=["PreTarget"])
app.include_router(OptionRouter, tags=["Options"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8888"))
    reload = os.environ.get("UVICORN_RELOAD", "true").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
