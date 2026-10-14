from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import library as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str | None = None, tag: str | None = None, db: AsyncSession = Depends(get_db)):
    prompts = await svc.list_prompts(db, q, tag)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Team Prompt Library", "prompts": prompts, "q": q or "", "tag": tag or ""})

@router.post("/ui/prompts")
async def ui_create(title: str = Form(...), body: str = Form(...), tags: str = Form(""), db: AsyncSession = Depends(get_db)):
    await svc.create_prompt(db, title, body, [t.strip() for t in tags.split(",") if t.strip()])
    return RedirectResponse("/", status_code=303)

@router.post("/ui/fork")
async def ui_fork(prompt_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.fork_prompt(db, prompt_id)
    return RedirectResponse("/", status_code=303)
