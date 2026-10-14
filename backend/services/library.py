from __future__ import annotations
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import SharedPrompt
from backend.utils.ids import short_id
from backend.utils.text import normalize

async def create_prompt(session: AsyncSession, title: str, body: str, tags: list[str] | None = None) -> SharedPrompt:
    tag_str = ",".join(sorted({t.strip().lower()[:32] for t in (tags or []) if t.strip()}))[:240]
    row = SharedPrompt(id=short_id(), title=title.strip()[:160], body=body.strip(), tags=tag_str)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_prompts(session: AsyncSession, q: str | None = None, tag: str | None = None) -> list[SharedPrompt]:
    stmt = select(SharedPrompt).order_by(SharedPrompt.created_at.desc())
    if tag:
        stmt = stmt.where(SharedPrompt.tags.contains(tag.lower()))
    rows = list((await session.execute(stmt)).scalars())
    if q:
        needle = normalize(q).lower()
        rows = [r for r in rows if needle in normalize(r.title + " " + r.body + " " + r.tags).lower()]
    return rows

async def rate_prompt(session: AsyncSession, prompt_id: str, stars: int) -> dict:
    row = await session.get(SharedPrompt, prompt_id)
    if not row:
        raise ValueError("prompt not found")
    stars = max(1, min(5, int(stars)))
    row.rating_sum += stars
    row.rating_count += 1
    await session.commit()
    avg = row.rating_sum / row.rating_count if row.rating_count else 0
    return {"prompt_id": row.id, "rating_avg": round(avg, 2), "rating_count": row.rating_count}

async def fork_prompt(session: AsyncSession, prompt_id: str, title: str | None = None) -> SharedPrompt:
    src = await session.get(SharedPrompt, prompt_id)
    if not src:
        raise ValueError("prompt not found")
    copy = SharedPrompt(
        id=short_id(),
        title=(title or f"Fork of {src.title}")[:160],
        body=src.body,
        tags=src.tags,
        fork_of=src.id,
    )
    session.add(copy)
    await session.commit()
    await session.refresh(copy)
    return copy
