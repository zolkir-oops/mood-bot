import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.init_db()


@app.get("/")
async def serve_app():
    return FileResponse("webapp/index.html")


@app.get("/api/entries/{year}/{month}")
async def get_month(year: int, month: int):
    rows = db.get_entries_for_month(year, month)
    return [dict(r) for r in rows]


@app.get("/api/entries/{year}/{month}/{day}")
async def get_day(year: int, month: int, day: int):
    rows = db.get_entries_for_day(year, month, day)
    return [dict(r) for r in rows]


@app.delete("/api/entries/{entry_id}")
async def delete(entry_id: int):
    entry = db.get_entry(entry_id)
    if not entry:
        raise HTTPException(404, "Not found")
    db.delete_entry(entry_id)
    return {"ok": True}


class UpdateBody(BaseModel):
    text: str


@app.patch("/api/entries/{entry_id}")
async def update(entry_id: int, body: UpdateBody):
    entry = db.get_entry(entry_id)
    if not entry:
        raise HTTPException(404, "Not found")
    db.update_entry_text(entry_id, body.text)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
