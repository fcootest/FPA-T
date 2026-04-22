"""FastAPI app entry (ISP S2)."""
from fastapi import FastAPI
from api.R20_routes import router as r20_router


app = FastAPI(title="FPA-T R20 API", version="1.0.1")
app.include_router(r20_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
