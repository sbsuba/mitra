"""
Mitra Signal Store MCP Server
Exposes SQLite signal history via MCP stdio transport.
Stores and retrieves 30-day check-in history per user.
"""
import sqlite3
import os
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Database path
DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "signals.db"
)

server = Server("signal-store")


def get_db():
    """Returns SQLite connection with signals table created."""
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            sleep TEXT,
            energy TEXT,
            social TEXT,
            mood TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    return db


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lists available signal store tools."""
    return [
        Tool(
            name="store_checkin",
            description="Store daily check-in signals for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "date": {"type": "string"},
                    "sleep": {"type": "string"},
                    "energy": {"type": "string"},
                    "social": {"type": "string"},
                    "mood": {"type": "string"},
                    "risk_score": {"type": "number"},
                    "risk_level": {"type": "string"}
                },
                "required": [
                    "user_id", "date", "sleep",
                    "energy", "social", "mood",
                    "risk_score", "risk_level"
                ]
            }
        ),
        Tool(
            name="get_history",
            description="Get last N days of check-ins for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "days": {"type": "number"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="get_trend",
            description="Get risk score trend for a user over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handles tool calls for signal store operations."""
    db = get_db()

    if name == "store_checkin":
        db.execute(
            """INSERT INTO signals
               (user_id, date, sleep, energy, social,
                mood, risk_score, risk_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                arguments["user_id"],
                arguments["date"],
                arguments["sleep"],
                arguments["energy"],
                arguments["social"],
                arguments["mood"],
                arguments["risk_score"],
                arguments["risk_level"]
            )
        )
        db.commit()
        return [TextContent(type="text", text="Check-in stored.")]

    elif name == "get_history":
        days = arguments.get("days", 7)
        cursor = db.execute(
            """SELECT date, sleep, energy, social, mood,
                      risk_score, risk_level
               FROM signals
               WHERE user_id = ?
               ORDER BY date DESC LIMIT ?""",
            (arguments["user_id"], days)
        )
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return [TextContent(type="text", text=str(result))]

    elif name == "get_trend":
        cursor = db.execute(
            """SELECT date, risk_score, risk_level
               FROM signals
               WHERE user_id = ?
               ORDER BY date DESC LIMIT 30""",
            (arguments["user_id"],)
        )
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return [TextContent(type="text", text=str(result))]

    return [TextContent(type="text", text="Unknown tool.")]


async def main():
    """Runs the MCP server over stdio."""
    async with stdio_server() as (read, write):
        init_options = server.create_initialization_options()
        await server.run(read, write, init_options)


if __name__ == "__main__":
    asyncio.run(main())
