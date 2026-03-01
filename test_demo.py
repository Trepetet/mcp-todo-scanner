#!/usr/bin/env python3
"""
Скрипт для быстрой проверки работы MCP сервера с demo_project
"""

import requests
import json
import sys

SERVER_URL = "http://localhost:8000"

def test_server():
    """Проверяет работу всех endpoints"""
    
    # 1. Проверка health
    print("1. Проверка health endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code == 200:
            print("   + Health check passed")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"   * Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   * Cannot connect to server: {e}")
        return False
    
    # 2. Сканирование demo_project
    print("\n2. Сканирование demo_project...")
    try:
        response = requests.post(
            f"{SERVER_URL}/scan",
            json={"path": "./demo_project"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   + Найдено TODO: {data.get('total', 0)}")
            print(f"   [] Путь: {data.get('scan_path')}")
            
            # Покажем первые 3 результата
            items = data.get('items', [])[:3]
            for item in items:
                print(f"      - {item['file']}:{item['line']} [{item['priority']}] {item['type']}")
        else:
            print(f"   * Scan failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   * Scan error: {e}")
        return False
    
    # 3. Анализ техдолга
    print("\n3. Анализ технического долга...")
    try:
        response = requests.post(
            f"{SERVER_URL}/analyze",
            json={"todos": data}
        )
        if response.status_code == 200:
            analysis = response.json()
            summary = analysis.get('summary', {})
            print(f"   + Анализ завершен")
            print(f"   # По приоритетам:")
            priorities = summary.get('by_priority', {})
            print(f"      HIGH: {priorities.get('HIGH', 0)}")
            print(f"      MEDIUM: {priorities.get('MEDIUM', 0)}")
            print(f"      LOW: {priorities.get('LOW', 0)}")
            
            # Проверим, что HIGH приоритетные на месте
            if priorities.get('HIGH', 0) > 0:
                print("   + Найдены критичные проблемы")
            else:
                print("   !! Критичные проблемы не найдены")
        else:
            print(f"   * Analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   * Analysis error: {e}")
        return False
    
    print("\n$ Все тесты пройдены успешно!")
    return True

if __name__ == "__main__":
    print("🔍 Тестирование Todo Scanner MCP Server\n")
    success = test_server()
    sys.exit(0 if success else 1)