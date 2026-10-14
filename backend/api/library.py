from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import library as svc

class PromptIn(BaseModel):
    title: str = Field(min_length=2)
    body: str = Field(min_length=4)
    tags: list[str] = Field(default_factory=list)

class RateIn(BaseModel):
    stars: int = Field(ge=1, le=5)

class ForkIn(BaseModel):
    title: str | None = None

router = APIRouter()

@router.get("/prompts")
async def prompts(q: str | None = None, tag: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_prompts(db, q, tag)
    return {
        "prompts": [
            {
                "id": p.id,
                "title": p.title,
                "body": p.body[:300],
                "tags": [t for t in p.tags.split(",") if t],
                "rating_avg": round(p.rating_sum / p.rating_count, 2) if p.rating_count else 0,
                "fork_of": p.fork_of,
            }
            for p in rows
        ]
    }

@router.post("/prompts")
async def create(payload: PromptIn, db: AsyncSession = Depends(get_db)):
    row = await svc.create_prompt(db, payload.title, payload.body, payload.tags)
    return {"id": row.id}

@router.post("/prompts/{prompt_id}/rate")
async def rate(prompt_id: str, payload: RateIn, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.rate_prompt(db, prompt_id, payload.stars)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.post("/prompts/{prompt_id}/fork")
async def fork(prompt_id: str, payload: ForkIn, db: AsyncSession = Depends(get_db)):
    try:
        row = await svc.fork_prompt(db, prompt_id, payload.title)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": row.id, "title": row.title}
