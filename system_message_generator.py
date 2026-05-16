#!/usr/bin/env python3
"""
Fetch tools from MCP server via HTTP (with session from header), print system prompt.
Usage: python system_message_generator.py http://localhost:8000/mcp
"""

import json
import sys
import urllib.request
from urllib.error import URLError


def make_request_and_get_headers(url: str, body: dict, session_id: str = None):
    """Makes a POST request and returns (response, headers) tuple."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers=headers,
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        headers_dict = dict(resp.headers.items())
        raw = b""
        for line in resp:
            if line.startswith(b"event: message") or line.startswith(b"data: "):
                raw += line
        # Извлекаем JSON из строки вида `data: {...}\n`
        for line in raw.split(b"\n"):
            if line.startswith(b"data: "):
                json_str = line[len(b"data: "):]
                return json.loads(json_str.decode("utf-8")), headers_dict
    except URLError as e:
        print(f"Error contacting MCP server: {e}", file=sys.stderr)
        sys.exit(1)


def extract_session_id(headers: dict) -> str:
    for k, v in headers.items():
        if k.lower() == "mcp-session-id":
            return v.strip()
    return None


def make_system_prompt(tools: list) -> str:
    lines = [
        "You have access to the following tools on the server.\n",
        "Use them when user asks to inspect, change, or debug the system.\n",
    ]
    for t in tools:
        name = t.get("name", "")
        desc = t.get("description", "").strip()
        if not desc:
            continue
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python system_message_generator.py <MCP_SERVER_URL>")
        print("Example: python system_message_generator.py http://localhost:8000/mcp")
        sys.exit(1)

    url = sys.argv[1]

    # 1. initialize → получаем заголовки и JSON
    init_resp, headers = make_request_and_get_headers(
        url,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "clientInfo": {
                    "name": "system-message-generator",
                    "version": "1.0.0",
                },
            },
        },
    )
    if "error" in init_resp:
        print(f"FAIL: initialize error: {init_resp['error']}", file=sys.stderr)
        sys.exit(1)

    session_id = extract_session_id(headers)
    if not session_id:
        print("FAIL: server did not return Mcp-Session-Id header", file=sys.stderr)
        sys.exit(1)

    print(f"MCP server initialized, Mcp-Session-Id: {session_id}", file=sys.stderr)

    # 2. notifications/initialized
    make_request_and_get_headers(
        url,
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        },
        session_id,
    )

    # 3. tools/list
    tools_resp, _ = make_request_and_get_headers(
        url,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        },
        session_id,
    )
    if "error" in tools_resp:
        print(f"FAIL: tools/list error: {tools_resp['error']}", file=sys.stderr)
        sys.exit(1)

    tools = tools_resp.get("result", {}).get("tools", [])
    if not tools:
        print("Warning: tools/list returned empty list.", file=sys.stderr)

    print(make_system_prompt(tools))
