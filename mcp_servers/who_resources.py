"""
Mitra WHO Resources MCP Server
Exposes global mental health crisis resources via MCP.
Resources sourced from WHO and verified crisis lines.
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from app.config import DISCLAIMER

server = Server("who-resources")

# Global crisis resources by country
CRISIS_RESOURCES = {
    "US": {
        "country": "United States",
        "helpline": "988 Suicide and Crisis Lifeline — call or text 988",
        "url": "https://988lifeline.org",
        "language": "en",
        "available": "24/7"
    },
    "IN": {
        "country": "India",
        "helpline": "iCall — 9152987821",
        "url": "https://icallhelpline.org",
        "language": "hi",
        "available": "Mon-Sat 8am-10pm IST"
    },
    "GB": {
        "country": "United Kingdom",
        "helpline": "Samaritans — 116 123",
        "url": "https://www.samaritans.org",
        "language": "en",
        "available": "24/7"
    },
    "AU": {
        "country": "Australia",
        "helpline": "Lifeline — 13 11 14",
        "url": "https://www.lifeline.org.au",
        "language": "en",
        "available": "24/7"
    },
    "CA": {
        "country": "Canada",
        "helpline": "Crisis Services Canada — 1-833-456-4566",
        "url": "https://www.crisisservicescanada.ca",
        "language": "en",
        "available": "24/7"
    },
    "ZA": {
        "country": "South Africa",
        "helpline": "SADAG — 0800 456 789",
        "url": "https://www.sadag.org",
        "language": "en",
        "available": "24/7"
    },
    "BR": {
        "country": "Brazil",
        "helpline": "CVV — 188",
        "url": "https://www.cvv.org.br",
        "language": "pt",
        "available": "24/7"
    },
    "MX": {
        "country": "Mexico",
        "helpline": "SAPTEL — 55 5259-8121",
        "url": "https://www.saptel.org.mx",
        "language": "es",
        "available": "24/7"
    },
    "DEFAULT": {
        "country": "International",
        "helpline": "International Association for Suicide Prevention",
        "url": "https://www.iasp.info/resources/Crisis_Centres/",
        "language": "en",
        "available": "Find your local crisis center"
    }
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lists available WHO resource tools."""
    return [
        Tool(
            name="get_crisis_resources",
            description=(
                "Get mental health crisis resources for a country. "
                "Returns helpline number, URL, and disclaimer."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "ISO country code e.g. US, IN, GB"
                    },
                    "language": {
                        "type": "string",
                        "description": "ISO language code e.g. en, hi, es"
                    }
                },
                "required": ["country"]
            }
        ),
        Tool(
            name="list_supported_countries",
            description="List all countries with crisis resources.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handles tool calls for WHO resource lookups."""
    if name == "get_crisis_resources":
        country = arguments.get("country", "DEFAULT")
        language = arguments.get("language", "en")
        resources = CRISIS_RESOURCES.get(
            country,
            CRISIS_RESOURCES["DEFAULT"]
        )
        result = {
            **resources,
            "language": language,
            "disclaimer": DISCLAIMER
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "list_supported_countries":
        countries = [
            {"code": k, "country": v["country"]}
            for k, v in CRISIS_RESOURCES.items()
            if k != "DEFAULT"
        ]
        return [TextContent(type="text", text=str(countries))]

    return [TextContent(type="text", text="Unknown tool.")]


async def main():
    """Runs the WHO resources MCP server over stdio."""
    async with stdio_server() as (read, write):
        init_options = server.create_initialization_options()
        await server.run(read, write, init_options)


if __name__ == "__main__":
    asyncio.run(main())
