from fastapi import FastAPI
import uvicorn
import re
from pathlib import Path
from typing import List
import json
from fastmcp import FastMCP
from datetime import datetime

# Создаем MCP сервер
mcp = FastMCP("Todo Scanner")

# Расширяем список расширений файлов для поиска
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp',
    '.c', '.h', '.hpp', '.php', '.rb', '.swift', '.kt', '.scala', '.md',
    '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.scss'
}

# Паттерны для поиска TODO комментариев
TODO_PATTERNS = [
    (r'#\s*(TODO|FIXME|HACK|BUG|OPTIMIZE|REFACTOR)(?:\(([^)]+)\))?:\s*(.*?)$', 'python,ruby,shell,yaml'),
    (r'//\s*(TODO|FIXME|HACK|BUG|OPTIMIZE|REFACTOR)(?:\(([^)]+)\))?:\s*(.*?)$', 'js,ts,java,go,c,cpp'),
    (r'/\*\s*(TODO|FIXME|HACK|BUG|OPTIMIZE|REFACTOR)(?:\(([^)]+)\))?:\s*(.*?)\*/', 'c,cpp,js,ts,java'),
    (r'<!--\s*(TODO|FIXME|HACK|BUG|OPTIMIZE|REFACTOR)(?:\(([^)]+)\))?:\s*(.*?)-->', 'html,xml'),
    (r'--\s*(TODO|FIXME|HACK|BUG|OPTIMIZE|REFACTOR)(?:\(([^)]+)\))?:\s*(.*?)$', 'sql')
]

DEFAULT_PRIORITIES = {
    'FIXME': 'HIGH',
    'BUG': 'HIGH',
    'HACK': 'HIGH',
    'TODO': 'MEDIUM',
    'OPTIMIZE': 'MEDIUM',
    'REFACTOR': 'MEDIUM'
}

HIGH_PRIORITY_KEYWORDS = [
    'security', 'vulnerability', 'exploit', 'crash', 'memory leak',
    'null pointer', 'deadlock', 'race condition', 'injection',
    'authentication', 'authorization', 'password', 'token', 'secret',
    'срочно', 'urgent', 'critical', 'important', 'важно', 'fix', 'bug'
]


@mcp.tool()
async def find_todos(path: str = "./demo_project", extensions: List[str] = None) -> str:
    results = []
    base_path = Path(path)

    if not base_path.exists():
        return json.dumps({"error": f"Path {path} does not exist"}, ensure_ascii=False, indent=2)

    target_exts = set(extensions) if extensions else CODE_EXTENSIONS

    for file_path in base_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in target_exts:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    for pattern, _ in TODO_PATTERNS:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            todo_type = match.group(1).upper()
                            author = match.group(2) if match.lastindex and match.lastindex >= 2 else None
                            comment = match.group(3) if match.lastindex and match.lastindex >= 3 else ""

                            results.append({
                                "file": str(file_path.relative_to(base_path)),
                                "line": i,
                                "type": todo_type,
                                "author": author,
                                "comment": comment.strip(),
                                "priority": DEFAULT_PRIORITIES.get(todo_type, 'LOW'),
                                "full_line": line.strip()
                            })
                            break
            except Exception as e:
                results.append({
                    "file": str(file_path.relative_to(base_path)),
                    "error": f"Failed to read file: {str(e)}"
                })

    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    results.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 999))

    return json.dumps({
        "total": len(results),
        "items": results,
        "scan_path": str(base_path),
        "timestamp": datetime.now().isoformat()
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def analyze_tech_debt(todos_json: str, custom_priority_keywords: List[str] = None) -> str:
    try:
        todos_data = json.loads(todos_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False, indent=2)

    if "items" not in todos_data:
        return json.dumps({"error": "Invalid todos format"}, ensure_ascii=False, indent=2)

    keywords = HIGH_PRIORITY_KEYWORDS.copy()
    if custom_priority_keywords:
        keywords.extend(custom_priority_keywords)

    items = todos_data["items"]

    for item in items:
        if "comment" in item:
            comment_lower = item["comment"].lower()

            if any(keyword.lower() in comment_lower for keyword in keywords):
                if item.get("priority") != "HIGH":
                    item["priority"] = "HIGH"
                    item["priority_reason"] = "Contains high-priority keywords"

            tags = []
            if "security" in comment_lower or "vulnerab" in comment_lower:
                tags.append("security")
            if "perf" in comment_lower or "slow" in comment_lower:
                tags.append("performance")
            if "bug" in comment_lower or "fix" in comment_lower or "crash" in comment_lower:
                tags.append("bug")
            if "test" in comment_lower:
                tags.append("testing")
            if "doc" in comment_lower:
                tags.append("documentation")

            item["tags"] = tags

    by_type = {}
    for item in items:
        t = item.get("type", "OTHER")
        by_type.setdefault(t, []).append(item)

    by_author = {}
    for item in items:
        author = item.get("author") or "unknown"
        by_author.setdefault(author, []).append(item)

    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    items.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 999))

    return json.dumps({
        "summary": {
            "total": todos_data.get("total", len(items)),
            "by_priority": {
                "HIGH": len([i for i in items if i.get("priority") == "HIGH"]),
                "MEDIUM": len([i for i in items if i.get("priority") == "MEDIUM"]),
                "LOW": len([i for i in items if i.get("priority") == "LOW"])
            },
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_author": {k: len(v) for k, v in by_author.items()}
        },
        "high_priority_first": [i for i in items if i.get("priority") == "HIGH"],
        "all_items": items,
        "analysis_timestamp": datetime.now().isoformat()
    }, ensure_ascii=False, indent=2)


@mcp.resource("config://priority-rules")
async def get_priority_rules() -> str:
    return json.dumps({
        "default_priorities": DEFAULT_PRIORITIES,
        "high_priority_keywords": HIGH_PRIORITY_KEYWORDS,
        "description": "HIGH: FIXME/BUG/HACK или содержит security/critical keywords. MEDIUM: обычные TODO. LOW: остальное"
    }, ensure_ascii=False, indent=2)


@mcp.prompt()
async def analyze_project_prompt(project_path: str) -> str:
    return f"""
    Проанализируй технический долг в проекте по пути {project_path}.

    1. Сначала найди все TODO маркеры используя find_todos
    2. Затем проанализируй их приоритеты используя analyze_tech_debt
    3. Составь отчет по результатам:
       - Сколько всего техдолга
       - Какие самые критичные проблемы
       - Кто главные "должники" (авторы)
       - Рекомендации по исправлению
    """


@mcp.tool()
async def health() -> str:
    return json.dumps({
        "status": "healthy",
        "service": "Todo Scanner MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

app = FastAPI(title="Todo Scanner MCP Server")

# MCP endpoint
app.mount("/mcp", mcp.http_app())

# --- ПРОСТОЙ REST HEALTH ---
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Todo Scanner MCP Server"
    }

# --- REST для find_todos ---
@app.post("/scan")
async def scan_project(path: str = "./demo_project"):
    result = await find_todos(path=path)
    return json.loads(result)

# --- REST для анализа ---
@app.post("/analyze")
async def analyze_project(todos: dict):
    result = await analyze_tech_debt(json.dumps(todos))
    return json.loads(result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)