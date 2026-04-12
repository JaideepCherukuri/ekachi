import asyncio
import os
import time
from pathlib import Path

import pytest
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("EKACHI_E2E_FRONTEND_URL")
BACKEND_URL = os.getenv("EKACHI_E2E_BACKEND_URL")


@pytest.mark.skipif(
    not (FRONTEND_URL and BACKEND_URL),
    reason="Set EKACHI_E2E_FRONTEND_URL and EKACHI_E2E_BACKEND_URL to run browser E2E coverage.",
)
@pytest.mark.asyncio
async def test_skill_library_example_template_flow():
    screenshot_path = Path("/tmp/ekachi-skill-library-browser-test.png")
    skill_name = f"Evidence Bundle Copy {int(time.time())}"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1480, "height": 1280})
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(f"{FRONTEND_URL}chat/control?tab=agents", wait_until="domcontentloaded")
        await page.get_by_role("button", name="Skills").click()
        await page.get_by_text("Skill Library", exact=True).wait_for(timeout=15000)
        await page.get_by_role("button", name="Example Skills").click()
        await page.get_by_text("Evidence Bundle", exact=True).wait_for(timeout=15000)

        await page.locator("article").filter(has_text="Evidence Bundle").get_by_role("button", name="Use Template").click()
        await page.get_by_text("Create Skill", exact=True).wait_for(timeout=15000)
        name_input = page.get_by_placeholder("Research Style")
        await name_input.fill(skill_name)
        await page.get_by_role("button", name="Create Skill").click()
        await page.get_by_text("Skill created", exact=False).wait_for(timeout=15000)

        response = await page.request.get(f"{BACKEND_URL}/api/v1/capabilities/skills")
        payload = await response.json()
        created_skill = next(skill for skill in payload["data"]["skills"] if skill["name"] == skill_name)
        assert created_skill["source"] == "user"
        assert created_skill["is_example"] is False

        await page.screenshot(path=str(screenshot_path), full_page=True)
        await browser.close()
