import asyncio
import os
from pathlib import Path
import time

import pytest
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("EKACHI_E2E_FRONTEND_URL")
BACKEND_URL = os.getenv("EKACHI_E2E_BACKEND_URL")


@pytest.mark.skipif(
    not (FRONTEND_URL and BACKEND_URL),
    reason="Set EKACHI_E2E_FRONTEND_URL and EKACHI_E2E_BACKEND_URL to run browser E2E coverage.",
)
@pytest.mark.asyncio
async def test_curated_connector_install_and_remove_flow():
    screenshot_path = Path("/tmp/ekachi-curated-connectors-browser-test.png")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(f"{FRONTEND_URL}chat/control?tab=connectors", wait_until="domcontentloaded")
        await page.get_by_text("Curated MCP Install Flows", exact=True).wait_for(timeout=15000)

        github_card = page.locator("article").filter(has=page.get_by_text("GitHub", exact=True)).first
        action_label = "Update" if await github_card.get_by_role("button", name="Update").count() else "Configure"
        await github_card.get_by_role("button", name=action_label).click()
        await page.get_by_text("Connector Editor", exact=True).wait_for(timeout=10000)
        if await page.get_by_placeholder("github_pat_...").count():
            await page.get_by_placeholder("github_pat_...").fill("github_pat_e2e_test_123")

        save_label = "Save Connector" if await page.get_by_role("button", name="Save Connector").count() else "Install Connector"
        await page.get_by_role("button", name=save_label).click()

        inventory_payload = None
        deadline = time.time() + 10
        while time.time() < deadline:
            inventory_response = await page.request.get(f"{BACKEND_URL}/api/v1/mcp/servers")
            inventory_payload = await inventory_response.json()
            if "github" in [server["name"] for server in inventory_payload["data"]["servers"]]:
                break
            await page.wait_for_timeout(250)

        assert inventory_payload is not None
        assert "github" in [server["name"] for server in inventory_payload["data"]["servers"]]

        connectors_response = await page.request.get(f"{BACKEND_URL}/api/v1/mcp/connectors")
        connectors_payload = await connectors_response.json()
        github_connector = next(
            connector for connector in connectors_payload["data"] if connector["connector_id"] == "github"
        )
        assert github_connector["configured"] is True

        server_response = await page.request.get(f"{BACKEND_URL}/api/v1/mcp/servers/github")
        server_payload = await server_response.json()
        assert server_payload["data"]["name"] == "github"
        assert server_payload["data"]["enabled"] is True

        await github_card.get_by_role("button", name="Remove").click()
        await page.get_by_text("Connector removed", exact=False).wait_for(timeout=15000)
        await page.screenshot(path=str(screenshot_path), full_page=True)
        await browser.close()
