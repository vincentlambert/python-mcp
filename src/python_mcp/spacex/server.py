import mcp.server.stdio
import mcp.types as types
import nest_asyncio
import spacexpy
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

nest_asyncio.apply()

server = Server("spacex")
spacex = spacexpy.SpaceX()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    print("*** handle_list_tools called")
    return [
        types.Tool(
            name="get-capsule-last-update",
            description="Get last update for a SpaceX capsule",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "Serial number of the capsule",
                    },
                },
                "required": ["serial"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can fetch weather data and notify clients of changes.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "get-capsule-last-update":
        serial = arguments.get("serial")
        if not serial:
            raise ValueError("Missing serial parameter")

        # Convert serial to uppercase to ensure consistent format
        serial = serial.upper()
        if len(serial) != 4:
            raise ValueError("Serial must be a four-character code (e.g. C106, C209)")

        # Basic serial validation
        # TODO
        pass

        # Get info for the capsule
        capsules = await spacex.capsules()
        capsule_text = None
        for capsule in capsules:
            if capsule["serial"] != serial:
                continue
            capsule_text = (
                f"Capsule serial number: {capsule['serial']}\n"
                f"Capsule type: {capsule['type']}\n"
                f"Capsule last update: {capsule['last_update']}\n"
            )
            break

        if not capsule_text:
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to retrieve information for capsule: {serial}.",
                )
            ]

        return [types.TextContent(type="text", text=capsule_text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def run():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="spacex",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
