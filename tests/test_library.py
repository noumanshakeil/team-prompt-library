import pytest

@pytest.mark.asyncio
async def test_prompt_fork_and_rate(client):
    p = await client.post("/api/prompts", json={"title": "Standup", "body": "Summarize blockers", "tags": ["team"]})
    pid = p.json()["id"]
    r = await client.post(f"/api/prompts/{pid}/rate", json={"stars": 5})
    assert r.json()["rating_count"] == 1
    f = await client.post(f"/api/prompts/{pid}/fork", json={})
    assert f.status_code == 200
