FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и демо-проект
COPY mcp_server.py .
COPY demo_project/ ./demo_project/

# Создаем smoke скрипт
RUN echo '#!/usr/bin/env python3\n\
import socket\n\
import sys\n\
import json\n\
try:\n\
    # Проверяем что процесс слушает порт\n\
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n\
    result = sock.connect_ex(("127.0.0.1", 8000))\n\
    if result == 0:\n\
        print("✅ MCP server is running and port 8000 is open")\n\
        sys.exit(0)\n\
    else:\n\
        print(f"❌ Port 8000 is not open (error code: {result})")\n\
        sys.exit(1)\n\
except Exception as e:\n\
    print(f"❌ Cannot connect to MCP server: {e}")\n\
    sys.exit(1)\n\
' > /usr/local/bin/smoke && chmod +x /usr/local/bin/smoke

EXPOSE 8000

# Запускаем сервер
CMD ["python", "mcp_server.py"]