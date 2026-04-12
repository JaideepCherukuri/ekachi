import asyncio
import json
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
async def test_workforce_creation_and_chat_worker_rendering():
    screenshot_path = Path("/tmp/ekachi-workforce-browser-test.png")
    worker_name = f"Live QA Worker {int(time.time())}"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(FRONTEND_URL, wait_until="domcontentloaded")
        await page.get_by_text("What can I do for you?", exact=False).wait_for(timeout=15000)
        await page.locator('[aria-haspopup="dialog"]:visible').first.hover()
        await page.locator(".z-50").get_by_text("Settings", exact=True).click()
        await page.get_by_text("Workforce", exact=True).click()
        await page.get_by_text("Workflow Lanes", exact=True).wait_for(timeout=15000)

        await page.get_by_role("button", name="New Worker").click()
        await page.get_by_placeholder("Research Worker").fill(worker_name)
        await page.get_by_role("combobox").nth(0).click()
        await page.get_by_text("Research", exact=True).last.click()
        await page.get_by_role("combobox").nth(1).click()
        await page.get_by_text("Research", exact=True).last.click()
        await page.get_by_placeholder("Owns evidence gathering and source validation.").fill(
            "Validates sources and keeps the task grounded."
        )
        await page.get_by_placeholder("search, browser, file").fill("search, browser")
        await page.get_by_placeholder(
            "Prefer primary sources, challenge unsupported claims, and hand off a concise evidence bundle to the next lane."
        ).fill("Use search and browser tools to gather evidence before implementation.")
        await page.get_by_role("button", name="Create Worker").click()
        await page.get_by_text("Worker created", exact=False).wait_for(timeout=15000)

        workers_response = await page.request.get(f"{BACKEND_URL}/api/v1/capabilities/workers")
        workers_payload = await workers_response.json()
        created_worker = next(worker for worker in workers_payload["data"]["workers"] if worker["name"] == worker_name)
        assert created_worker["role"] == "research"
        assert created_worker["lane"] == "research"
        assert created_worker["tool_names"] == ["search", "browser"]

        session_response = await page.request.put(f"{BACKEND_URL}/api/v1/sessions", data={})
        session_payload = await session_response.json()
        session_id = session_payload["data"]["session_id"]

        await page.goto(f"{FRONTEND_URL}chat/{session_id}", wait_until="domcontentloaded")
        await page.get_by_text("Workers", exact=True).last.click()
        await page.get_by_text("Workers Workspace", exact=True).wait_for(timeout=15000)
        await page.locator("div,span").filter(has_text=worker_name).first.wait_for(timeout=15000)
        await page.screenshot(path=str(screenshot_path), full_page=True)
        await browser.close()
