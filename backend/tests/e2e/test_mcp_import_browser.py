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
async def test_mcp_import_and_export_flow():
    screenshot_path = Path("/tmp/ekachi-mcp-import-browser-test.png")
    local_server_name = f"local-import-{int(time.time())}"
    remote_server_name = f"remote-import-{int(time.time())}"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1480, "height": 1280})
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(f"{FRONTEND_URL}chat/control?tab=connectors", wait_until="domcontentloaded")
        await page.get_by_text("Import Local MCP JSON", exact=True).wait_for(timeout=15000)

        import_payload = {
            "mcpServers": {
                local_server_name: {
                    "transport": "stdio",
                    "enabled": True,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                }
            }
        }
        await page.get_by_placeholder('{"mcpServers":{"filesystem":{"command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","/tmp"],"transport":"stdio","enabled":true}}}').fill(json.dumps(import_payload))
        await page.get_by_role("button", name="Import JSON").click()

        deadline = time.time() + 10
        server_names: list[str] = []
        while time.time() < deadline:
            inventory_response = await page.request.get(f"{BACKEND_URL}/api/v1/mcp/servers")
            inventory_payload = await inventory_response.json()
            server_names = [server["name"] for server in inventory_payload["data"]["servers"]]
            if local_server_name in server_names:
                break
            await page.wait_for_timeout(250)
        assert local_server_name in server_names

        await page.get_by_placeholder("acme-mcp").fill(remote_server_name)
        await page.get_by_placeholder("https://mcp.example.com/server").fill("https://mcp.example.com/server")
        await page.get_by_placeholder("Hosted MCP endpoint").fill("Hosted regression server")
        await page.get_by_role("button", name="Import Remote Server").click()

        deadline = time.time() + 10
        server_names = []
        while time.time() < deadline:
            inventory_response = await page.request.get(f"{BACKEND_URL}/api/v1/mcp/servers")
            inventory_payload = await inventory_response.json()
            server_names = [server["name"] for server in inventory_payload["data"]["servers"]]
            if remote_server_name in server_names:
                break
            await page.wait_for_timeout(250)
        assert remote_server_name in server_names

        await page.get_by_role("button", name="Refresh Export JSON").click()
        export_text = await page.get_by_placeholder('{"mcpServers":{}}').input_value()
        assert local_server_name in export_text
        assert remote_server_name in export_text

        await page.screenshot(path=str(screenshot_path), full_page=True)
        await browser.close()
