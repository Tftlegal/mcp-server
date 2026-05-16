#!/bin/bash

cd /root/mcp-server

# Активируем виртуальное окружение (если venv ещё нет — создать)
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Установка/обновление зависимостей
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Запуск MCP‑сервера
fastmcp run mcp_server.py:mcp --transport http --host 0.0.0.0 --port 8000
