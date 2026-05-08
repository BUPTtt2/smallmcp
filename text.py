import sys
print("Script started", file=sys.stderr)
try:
    from fastmcp import FastMCP
    print("Imported FastMCP", file=sys.stderr)
except Exception as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("Test")
print("MCP instance created", file=sys.stderr)

if __name__ == "__main__":
    print("Entering run loop", file=sys.stderr)
    mcp.run(transport="stdio")