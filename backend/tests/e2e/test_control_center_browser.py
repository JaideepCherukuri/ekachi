import os
import time
from pathlib import Path
from urllib.parse import quote

import pytest
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("EKACHI_E2E_FRONTEND_URL")
BACKEND_URL = os.getenv("EKACHI_E2E_BACKEND_URL")


@pytest.mark.skipif(
    not (FRONTEND_URL and BACKEND_URL),
    reason="Set EKACHI_E2E_FRONTEND_URL and EKACHI_E2E_BACKEND_URL to run browser E2E coverage.",
)
@pytest.mark.asyncio
async def test_control_center_project_and_memory_flow():
    screenshot_path = Path("/tmp/ekachi-control-center-browser-test.png")
    project_name = f"Parity Project {int(time.time())}"
    memory_text = f"Control center memory regression {int(time.time())}"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1480, "height": 1280})

        await page.goto(f"{FRONTEND_URL}chat/control?tab=projects", wait_until="domcontentloaded")
        await page.locator("h1").filter(has_text="Eigent-style workspace surfaces").wait_for(timeout=15000)

        await page.get_by_placeholder("Go-to-market launch").fill(project_name)
        await page.get_by_role("button", name="Create Project").click()
        await page.get_by_text("Project created", exact=False).wait_for(timeout=15000)
        project_card = page.locator("article").filter(has_text=project_name).first
        await project_card.wait_for(timeout=15000)
        await project_card.get_by_role("button").first.click()

        projects_response = await page.request.get(f"{BACKEND_URL}/api/v1/projects")
        projects_payload = await projects_response.json()
        created_project = next(
            project for project in projects_payload["data"]["projects"] if project["name"] == project_name
        )

        await page.get_by_role("button", name="Agents").click()
        await page.get_by_role("button", name="Memory").click()
        await page.get_by_text(f"Editing memory for {project_name}.", exact=True).wait_for(timeout=15000)
        memory_box = page.get_by_placeholder(
            "Critical facts, project constraints, stakeholders, or preferences that should persist across future sessions."
        )
        await memory_box.fill(memory_text)
        await page.get_by_role("button", name="Save Memory").click()
        await page.get_by_text("Project memory saved", exact=False).wait_for(timeout=15000)

        memory_response = await page.request.get(
            f"{BACKEND_URL}/api/v1/capabilities/memory?project_id={quote(created_project['project_id'])}"
        )
        memory_payload = await memory_response.json()
        assert memory_payload["data"]["content"] == memory_text

        await page.goto(f"{FRONTEND_URL}chat/control?tab=connectors", wait_until="domcontentloaded")
        await page.get_by_text("Curated MCP Install Flows", exact=True).wait_for(timeout=15000)

        await page.goto(f"{FRONTEND_URL}chat/control?tab=browser", wait_until="domcontentloaded")
        await page.get_by_text("Live Browser Cookies", exact=True).wait_for(timeout=15000)

        await page.goto(f"{FRONTEND_URL}chat/control?tab=settings", wait_until="domcontentloaded")
        await page.get_by_role("button", name="Privacy").click()
        await page.get_by_text("Privacy Controls", exact=True).wait_for(timeout=15000)

        await page.screenshot(path=str(screenshot_path), full_page=True)
        await browser.close()
