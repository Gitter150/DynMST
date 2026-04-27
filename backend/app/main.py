from __future__ import annotations

from fastapi import FastAPI

from app.api.mst import router as mst_router

app = FastAPI(title="Dynamic MST Backend", version="0.1.0")
app.include_router(mst_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
