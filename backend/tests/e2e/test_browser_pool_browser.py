import asyncio
import os
import requests
import shutil
import subprocess
import tempfile
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
async def test_browser_pool_add_and_activate_flow():
    screenshot_path = Path("/tmp/ekachi-browser-pool-browser-test.png")
    browser_label = f"Local Pool Browser {int(time.time())}"
    project_name = f"Browser Pool Project {int(time.time())}"
    port = 9322
    user_data_dir = tempfile.mkdtemp(prefix="ekachi-browser-pool-")
    browser_process: subprocess.Popen[str] | None = None

    async with async_playwright() as playwright:
        try:
            executable = playwright.chromium.executable_path
            browser_process = subprocess.Popen(
                [
                    executable,
                    f"--remote-debugging-port={port}",
                    f"--user-data-dir={user_data_dir}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--no-sandbox",
                    "--headless=new",
                    "about:blank",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            await asyncio.sleep(2)

            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1480, "height": 1280})
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

            await page.goto(f"{FRONTEND_URL}chat/control?tab=projects", wait_until="domcontentloaded")
            await page.get_by_placeholder("Go-to-market launch").fill(project_name)
            await page.get_by_role("button", name="Create Project").click()
            await page.get_by_text("Project created", exact=False).wait_for(timeout=15000)
            project_id = next(
                project["project_id"]
                for project in requests.get(f"{BACKEND_URL}/api/v1/projects", timeout=10).json()["data"]["projects"]
                if project["name"] == project_name
            )

            await page.goto(f"{FRONTEND_URL}chat/control?tab=browser", wait_until="domcontentloaded")
            await page.get_by_text("Browser Pool", exact=True).wait_for(timeout=15000)

            await page.get_by_placeholder("Local Login Browser").fill(browser_label)
            await page.get_by_placeholder("http://127.0.0.1:9222").fill(f"http://127.0.0.1:{port}")
            await page.get_by_role("button", name="Add Browser").click()
            await page.get_by_text("Browser added to pool", exact=False).wait_for(timeout=15000)
            await page.get_by_text(browser_label, exact=True).wait_for(timeout=15000)

            deadline = time.time() + 15
            pool_payload = None
            while time.time() < deadline:
                pool_response = requests.get(
                    f"{BACKEND_URL}/api/v1/browser/projects/{project_id}/pool",
                    timeout=10,
                )
                pool_payload = pool_response.json()
                browsers = pool_payload["data"]["browsers"]
                if any(browser["label"] == browser_label and browser["healthy"] for browser in browsers):
                    break
                await page.wait_for_timeout(250)

            assert pool_payload is not None
            assert any(browser["label"] == browser_label and browser["healthy"] for browser in pool_payload["data"]["browsers"])

            await page.screenshot(path=str(screenshot_path), full_page=True)
            await browser.close()
        finally:
            if browser_process is not None:
                browser_process.terminate()
                try:
                    browser_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    browser_process.kill()
            shutil.rmtree(user_data_dir, ignore_errors=True)
