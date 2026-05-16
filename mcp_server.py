#!/usr/bin/env python3
"""
FastMCP server with apt, Python and Kali tools.

Запуск:
    fastmcp run mcp_server.py:mcp --transport http --port 8000

Логирование:
    KALI_MCP_LOG_LEVEL=INFO
    KALI_MCP_LOG_LEVEL=DEBUG

Важно:
- tools/list и tools/call должны работать через MCP session:
  initialize -> Mcp-Session-Id -> notifications/initialized -> tools/list -> tools/call
- run_command принимает аргумент cmd, не command
"""

import json
import logging
import os
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.tools import tool

mcp = FastMCP("Kali MCP Server")

LOG_LEVEL = os.getenv("KALI_MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s — %(levelname)s — %(name)s — %(message)s",
)
logger = logging.getLogger("kali_mcp")

COMMAND_TIMEOUT = int(os.getenv("KALI_MCP_COMMAND_TIMEOUT", "120"))


def _short(s: str, limit: int = 2000) -> str:
    if s is None:
        return ""
    return s if len(s) <= limit else s[:limit] + "\n... [TRUNCATED]"


def run_shell(cmd: str) -> Dict[str, Any]:
    """
    Запускает shell command безопаснее:
    - shlex.split для аргументов
    - таймаут
    - возврат structured JSON
    """
    logger.debug(f"run_shell cmd={cmd!r}")
    try:
        argv = shlex.split(cmd)
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT,
        )
        payload = {
            "success": result.returncode == 0,
            "cmd": cmd,
            "returncode": result.returncode,
            "stdout": _short(result.stdout),
            "stderr": _short(result.stderr),
        }
        if result.returncode == 0:
            logger.debug(f"run_shell success cmd={cmd!r}")
        else:
            logger.warning(f"run_shell non-zero cmd={cmd!r} rc={result.returncode}")
        return payload
    except subprocess.TimeoutExpired:
        logger.error(f"run_shell timeout cmd={cmd!r}")
        return {
            "success": False,
            "cmd": cmd,
            "error": f"Command timed out after {COMMAND_TIMEOUT}s",
            "stderr": f"Command timed out after {COMMAND_TIMEOUT}s",
        }
    except FileNotFoundError as e:
        logger.error(f"run_shell file not found cmd={cmd!r}: {e}")
        return {
            "success": False,
            "cmd": cmd,
            "error": str(e),
            "stderr": str(e),
        }
    except Exception as e:
        logger.exception(f"run_shell error cmd={cmd!r}")
        return {
            "success": False,
            "cmd": cmd,
            "error": str(e),
            "stderr": str(e),
        }


@tool
def system_apt(action: str, packages: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run apt package manager operations: install, remove, update, upgrade.
    """
    logger.info(f"system_apt action={action!r} packages={packages!r}")

    if action == "update":
        cmd = "apt update"
    elif action == "upgrade":
        cmd = "apt upgrade -y"
    elif action == "install" and packages:
        cmd = f"apt install -y {' '.join(packages)}"
    elif action == "remove" and packages:
        cmd = f"apt remove -y {' '.join(packages)}"
    else:
        return {
            "success": False,
            "error": "Invalid action or missing packages",
            "allowed_actions": ["install", "remove", "update", "upgrade"],
        }

    return run_shell(cmd)


@tool
def run_python(code: str) -> Dict[str, Any]:
    """
    Run arbitrary Python code on the server.
    """
    logger.info("run_python called")
    try:
        compiled = compile(code, "<mcp>", "exec")
        g = {"__builtins__": __builtins__}
        l = {}
        exec(compiled, g, l)
        return {
            "success": True,
            "stdout": "Code executed",
            "locals": {k: str(v) for k, v in l.items() if not k.startswith("__")},
        }
    except Exception as e:
        logger.exception("run_python failed")
        return {"success": False, "stderr": str(e)}


@tool
def run_command(cmd: str) -> Dict[str, Any]:
    """
    Run arbitrary shell command (Kali, wireless, etc.).
    """
    logger.info(f"run_command cmd={cmd!r}")
    return run_shell(cmd)


@tool
def airmon_setup(interface: str) -> Dict[str, Any]:
    """
    Create monitor interface using airmon-ng.
    """
    logger.info(f"airmon_setup interface={interface!r}")
    return run_shell(f"airmon-ng start {shlex.quote(interface)}")


@tool
def iwconfig(interface: str = None) -> Dict[str, Any]:
    """
    Show wireless interface config via iwconfig.
    """
    logger.info(f"iwconfig interface={interface!r}")
    cmd = "iwconfig"
    if interface:
        cmd += f" {shlex.quote(interface)}"
    return run_shell(cmd)


@tool
def ifconfig(interface: str = None) -> Dict[str, Any]:
    """
    Show network interface config via ifconfig.
    """
    logger.info(f"ifconfig interface={interface!r}")
    cmd = "ifconfig"
    if interface:
        cmd += f" {shlex.quote(interface)}"
    return run_shell(cmd)


@tool
def ip_show(link_or_route: str = "link") -> Dict[str, Any]:
    """
    Use ip to show link/route information.
    """
    logger.info(f"ip_show link_or_route={link_or_route!r}")
    if link_or_route not in ("link", "route"):
        return {"success": False, "error": "link_or_route must be 'link' or 'route'"}
    return run_shell(f"ip {link_or_route}")


@tool
def wash_scan(
    interface: str,
    channel: int = None,
    sort_by: str = None,
    all: bool = False,
    ignore_frame_errors: bool = False,
) -> Dict[str, Any]:
    """
    Run wash to scan for WPS networks.
    """
    logger.info(
        "wash_scan interface=%r channel=%r sort_by=%r all=%r ignore_frame_errors=%r",
        interface, channel, sort_by, all, ignore_frame_errors
    )
    cmd = ["wash", "-i", interface]
    if channel is not None:
        cmd.extend(["-c", str(channel)])
    if sort_by:
        cmd.extend(["--sort-by", sort_by])
    if all:
        cmd.append("-a")
    if ignore_frame_errors:
        cmd.append("-C")
    return run_shell(" ".join(cmd))


@tool
def airodump_monitor(interface: str, show_wps: bool = False) -> Dict[str, Any]:
    """
    Run airodump-ng to monitor networks (with or without WPS column).
    """
    logger.info(f"airodump_monitor interface={interface!r} show_wps={show_wps!r}")
    cmd = ["airodump-ng", interface]
    if show_wps:
        cmd.append("--wps")
    return run_shell(" ".join(cmd))


@tool
def wifite_wps_only(
    interface: str = None,
    channel: int = None,
    ignore_locks: bool = False,
) -> Dict[str, Any]:
    """
    Run wifite for WPS-only attacks (PIN + Pixie-Dust).
    """
    logger.info(
        "wifite_wps_only interface=%r channel=%r ignore_locks=%r",
        interface, channel, ignore_locks
    )
    cmd = ["wifite", "--wps-only"]
    if interface:
        cmd.extend(["-i", interface])
    if channel is not None:
        cmd.extend(["-c", str(channel)])
    if ignore_locks:
        cmd.append("--ignore-locks")
    return run_shell(" ".join(cmd))


@tool
def reaver_pixie(
    interface: str,
    bssid: str,
    channel: int,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run reaver with Pixie-Dust attack.
    """
    logger.info(
        "reaver_pixie interface=%r bssid=%r channel=%r verbose=%r",
        interface, bssid, channel, verbose
    )
    cmd = ["reaver", "-i", interface, "-b", bssid, "-c", str(channel), "-K", "1"]
    if verbose:
        cmd.append("-vv")
    return run_shell(" ".join(cmd))


@tool
def hcxdumptool_scan(
    interface: str,
    duration: int = 30,
    out: str = "/tmp/wifi.pcapng",
) -> Dict[str, Any]:
    """
    Run hcxdumptool to capture WPA handshakes.
    """
    logger.info(
        "hcxdumptool_scan interface=%r duration=%r out=%r",
        interface, duration, out
    )
    #cmd = ["hcxdumptool", "-i", interface, "-o", out, "-c", str(duration)]
    cmd = ["hcxdumptool", "-i", interface, "-w", out, "-c", str(duration)]
    return run_shell(" ".join(cmd))


# Register tools explicitly for clarity
mcp.tool(system_apt)
mcp.tool(run_python)
mcp.tool(run_command)
mcp.tool(airmon_setup)
mcp.tool(iwconfig)
mcp.tool(ifconfig)
mcp.tool(ip_show)
mcp.tool(wash_scan)
mcp.tool(airodump_monitor)
mcp.tool(wifite_wps_only)
mcp.tool(reaver_pixie)
mcp.tool(hcxdumptool_scan)


if __name__ == "__main__":
    from fastmcp.cli import mcp_export
    mcp_export("mcp", mcp)
