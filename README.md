# MCP KALI SERVER


Ошибка 400 Bad Request: Missing session ID означает, что MCP‑серверу в streamable-http‑режиме нужен жизненный цикл сессии: сначала initialize, затем initialized, и только потом tools/list уже с заголовком Mcp-Session-Id.
Ниже — пошаговая цепочка curl.


#KALI_MCP_SERVER_URL=192.168.0.100:3002/mcp
KALI_MCP_SERVER_URL=192.168.0.100:8000/mcp

## Start 
```
fastmcp run mcp_server.py:mcp \
  --transport http \
  --host 192.168.0.100 \
  --port 8000
```

#Запуск на локалхосте
```
fastmcp run mcp_server.py:mcp --transport http  --port 8000
```

#Запуск на конкретном IP
```
fastmcp run mcp_server.py:mcp --transport http --host 192.168.0.100 --port 8000
```

#Запуск на всех нитерфейсах
```
fastmcp run mcp_server.py:mcp --transport http --host 0.0.0.0  --port 8000 
```

#CURL

1. Шаг 1: initialize и получение Mcp-Session-Id
```bash

curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -D headers.txt \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "tools": {},
        "resources": {},
        "prompts": {}
      },
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }'
```

```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -D headers.txt \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "tools": {},
        "resources": {},
        "prompts": {}
      },
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }'
```
После выполнения headers.txt будет содержать строку примерно такую:

Mcp-Session-Id: 123e4567-e89b-12d3-a456-426614174000

Извлекаешь SESSION_ID так:
```
SESSION_ID=$(grep -i "mcp-session-id" headers.txt | cut -d' ' -f2 | tr -d '\r')
```
echo "Session ID: $SESSION_ID"
2. Шаг 2: initialized (уведомление)

```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```
INFO:     192.168.0.100:38182 - "POST /mcp HTTP/1.1" 202 Accepted

```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

3. Шаг 3: tools/list с сессией
Теперь запрос к tools/list пройдёт успешно:


```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

Этот запрос вернёт примерно такой JSON‑массив инструментов:
```json
event: message
data: {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"system_apt","description":"Run apt package manager operations: install, remove, update, upgrade.","inputSchema":{"additionalProperties":false,"properties":{"action":{"type":"string","description":"One of: \"install\", \"remove\", \"update\", \"upgrade\""},"packages":{"default":null,"items":{"type":"string"},"type":"array","description":"List of package names (for install/remove)"}},"required":["action"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"run_python","description":"Run arbitrary Python code on the server.","inputSchema":{"additionalProperties":false,"properties":{"code":{"type":"string","description":"Python source code as string."}},"required":["code"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"run_command","description":"Run arbitrary shell command (Kali, wireless, etc.).","inputSchema":{"additionalProperties":false,"properties":{"cmd":{"type":"string","description":"Shell command string (e.g. 'airodump-ng wlp8s1mon')."}},"required":["cmd"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"airmon_setup","description":"Create monitor interface using airmon-ng.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"type":"string","description":"Base interface (e.g. 'wlan0', 'wlp8s1')."}},"required":["interface"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"iwconfig","description":"Show wireless interface config via iwconfig.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"default":null,"type":"string","description":"Interface name (optional)."}},"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"ifconfig","description":"Show network interface config via ifconfig.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"default":null,"type":"string","description":"Interface name (optional)."}},"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"ip_show","description":"Use ip to show link/route information.","inputSchema":{"additionalProperties":false,"properties":{"link_or_route":{"default":"link","type":"string","description":"'link' or 'route'."}},"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"wash_scan","description":"Run wash to scan for WPS networks.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"type":"string","description":"Monitor interface (e.g. 'wlp8s1mon')."},"channel":{"default":null,"type":"integer","description":"Optional channel number."},"sort_by":{"default":null,"type":"string","description":"Field to sort by (e.g. 'signal')."},"all":{"default":false,"type":"boolean","description":"If True, show all networks, not just WPS."},"ignore_frame_errors":{"default":false,"type":"boolean","description":"Pass -C to ignore frame errors."}},"required":["interface"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"airodump_monitor","description":"Run airodump-ng to monitor networks (with or without WPS column).","inputSchema":{"additionalProperties":false,"properties":{"interface":{"type":"string","description":"Monitor interface (e.g. 'wlp8s1mon')."},"show_wps":{"default":false,"type":"boolean","description":"If True, show WPS column."}},"required":["interface"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"wifite_wps_only","description":"Run wifite for WPS‑only attacks (PIN + Pixie‑Dust).","inputSchema":{"additionalProperties":false,"properties":{"interface":{"default":null,"type":"string","description":"Monitor interface (optional)."},"channel":{"default":null,"type":"integer","description":"Optional channel."},"ignore_locks":{"default":false,"type":"boolean","description":"If True, ignore WPS lockouts."}},"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"reaver_pixie","description":"Run reaver with Pixie‑Dust attack.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"type":"string","description":"Monitor interface (e.g. 'wlp8s1mon')."},"bssid":{"type":"string","description":"Target BSSID."},"channel":{"type":"integer","description":"Channel."},"verbose":{"default":true,"type":"boolean","description":"If True, use -vv."}},"required":["interface","bssid","channel"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}},{"name":"hcxdumptool_scan","description":"Run hcxdumptool to capture WPA handshakes.","inputSchema":{"additionalProperties":false,"properties":{"interface":{"type":"string","description":"Interface in monitor mode."},"duration":{"default":30,"type":"integer","description":"Capture duration in seconds."},"out":{"default":"/tmp/wifi.pcapng","type":"string","description":"Output pcapng file."}},"required":["interface"],"type":"object"},"outputSchema":{"additionalProperties":true,"type":"object"},"_meta":{"fastmcp":{"tags":[]}}}]}}
```


#После инициализации должна появиться возможность использования KALI MCP-сервера:

4) system_apt update
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "system_apt",
      "arguments": {
        "action": "update"
      }
    }
  }'
```

5) system_apt install
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "system_apt",
      "arguments": {
        "action": "install",
        "packages": ["aircrack-ng", "hcxtools"]
      }
    }
  }'
```
6) run_python

```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "run_python",
      "arguments": {
        "code": "print(2+2)"
      }
    }
  }'
```
7) run_command
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "run_command",
      "arguments": {
        "cmd": "iwconfig"
      }
    }
  }'
```
8) airmon_setup
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "airmon_setup",
      "arguments": {
        "interface": "wlp8s1"
      }
    }
  }'
```
9) wash_scan
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "tools/call",
    "params": {
      "name": "wash_scan",
      "arguments": {
        "interface": "wlp8s1mon",
        "sort_by": "signal",
        "ignore_frame_errors": true
      }
    }
  }'
```
10) airodump_monitor
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 9,
    "method": "tools/call",
    "params": {
      "name": "airodump_monitor",
      "arguments": {
        "interface": "wlp8s1mon",
        "show_wps": true
      }
    }
  }'
```
11) hcxdumptool_scan
```bash
curl -X POST $KALI_MCP_SERVER_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/call",
    "params": {
      "name": "hcxdumptool_scan",
      "arguments": {
        "interface": "wlp8s1mon",
        "duration": 60,
        "out": "/tmp/wifi.pcapng"
      }
    }
  }'
```

Ниже даю обновлённый mcp_server.py с нормальным logging, более безопасным run_shell, удобной отладкой и аккуратной регистрацией tools через FastMCP.
Также дам набор рабочих curl-примеров для initialize, tools/list, tools/call, и пример OpenAPI-спеки для HTTP-обёртки, если тебе нужно документировать endpoint отдельно.

## Пример OpenAPI-спеки

Если ты хочешь документировать именно HTTP API MCP endpoint как внешний сервис, можно описать его одной POST /mcp операцией, но учти: это не “классический REST”, а JSON-RPC поверх MCP.


### Ниже упрощённая OpenAPI 3.0 схема для твоего endpoint.

```text
openapi: 3.0.3
info:
  title: Kali MCP Server
  version: 1.0.0
  description: MCP JSON-RPC HTTP endpoint for Kali wireless tools
servers:
  - url: http://192.168.0.100:3002
paths:
  /mcp:
    post:
      summary: MCP JSON-RPC endpoint
      description: Initialize session, list tools, and call tools through MCP JSON-RPC
      requestBody:
        required: true
        content:
          application/json:
            schema:
              oneOf:
                - $ref: '#/components/schemas/InitializeRequest'
                - $ref: '#/components/schemas/NotificationsInitializedRequest'
                - $ref: '#/components/schemas/ToolsListRequest'
                - $ref: '#/components/schemas/ToolsCallRequest'
      responses:
        '200':
          description: MCP response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/McpResponse'
        '202':
          description: Accepted
        '400':
          description: Bad Request
        '500':
          description: Server Error
components:
  schemas:
    InitializeRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          example: "2.0"
        id:
          type: integer
          example: 1
        method:
          type: string
          example: initialize
        params:
          type: object
          properties:
            protocolVersion:
              type: string
              example: "2024-11-05"
            capabilities:
              type: object
            clientInfo:
              type: object
      required: [jsonrpc, id, method, params]

    NotificationsInitializedRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          example: "2.0"
        method:
          type: string
          example: notifications/initialized
      required: [jsonrpc, method]

    ToolsListRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          example: "2.0"
        id:
          type: integer
          example: 2
        method:
          type: string
          example: tools/list
        params:
          type: object
      required: [jsonrpc, id, method]

    ToolsCallRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          example: "2.0"
        id:
          type: integer
          example: 3
        method:
          type: string
          example: tools/call
        params:
          type: object
          properties:
            name:
              type: string
            arguments:
              type: object
      required: [jsonrpc, id, method, params]

    McpResponse:
      type: object
      properties:
        jsonrpc:
          type: string
        id:
          type: integer
        result:
          type: object
        error:
          type: object
```

## Что дальше стоит поправить?

Сейчас у тебя главная причина 400 Bad Request — несоответствие имен аргументов в бот-коде и schema MCP tools.
Нужно синхронизировать kali_handlers.py с tools/list: например, run_command должен передавать cmd, airodump_monitor — show_wps, wifite_wps_only — interface/channel/ignore_locks, reaver_pixie — обязательные interface/bssid/channel.
Ниже — корректный systemd‑юнит, который:
запускает твой /root/mcp_server.sh,
логирует всё в journalctl,
при желании можно перенаправить отдельно в /var/log/mcp_server.log.

1. Юнит /etc/systemd/system/mcp_server.service
```text
[Unit]
Description=Kali MCP Server for llama.cpp
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/root

# Указываем путь к вашему скрипту
ExecStart=/root/mcp_server.sh

# Автостарт после перезагрузки
Restart=always
RestartSec=5

# Журнал systemd (journalctl)
StandardOutput=journal
StandardError=journal

# Если хочешь дополнительно писать в файл:
# StandardOutput=append:/var/log/mcp_server.log
# StandardError=append:/var/log/mcp_server.log

# Ограничения безопасности (по желанию)
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
2. Что поменять в mcp_server.sh (для systemd)
systemd запускается не в интерактивной оболочке, поэтому лучше явно указать путь к python3, pip, fastmcp:

```bash
#!/bin/bash

cd /root

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
```

3. Установка и запуск юнита
```bash
# 1. Отредактируй /etc/systemd/system/mcp_server.service
nano /etc/systemd/system/mcp_server.service

# 2. Перечитать конфиги
systemctl daemon-reexec
systemctl daemon-reload

# 3. Включить автозапуск и запустить
systemctl enable mcp_server.service
systemctl start mcp_server.service

# 4. Проверить статус
systemctl status mcp_server.service
```
4. Просмотр логов
Через journalctl:

```bash
journalctl -u mcp_server.service -f
```
Если в юните включить:

```text
StandardOutput=append:/var/log/mcp_server.log
StandardError=append:/var/log/mcp_server.log
```
то логи будут дополнительно писаться в:

```bash
tail -f /var/log/mcp_server.log
```

4. Что делать в system_message_generator.py ?
Твой system_message_generator.py нужно немного допилить, чтобы он:
делал initialize → ловил Mcp-Session-Id из заголовков,
шлёл notify/initialized,
только затем запрашивал tools/list.
