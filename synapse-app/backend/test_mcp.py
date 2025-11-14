"""
Quick test to validate MCP server imports and setup
"""

import sys

print("Testing MCP server imports...")

try:
    # Test MCP imports
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("[OK] MCP imports successful")

    # Test Synapse service imports
    from app.services.llm_client import get_llm_client
    from app.services.qdrant_client import get_qdrant_client
    from app.services.supabase_client import get_supabase_client
    print("[OK] Synapse service imports successful")

    # Test MCP server creation
    import asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    app = Server("synapse-chat-storage-test")
    print("[OK] MCP Server object created")

    print("\n=== MCP Server Validation PASSED ===")
    print("The MCP server is ready to use!")
    print("\nNext steps:")
    print("1. Create the chat_records table in Supabase (run create_chat_table.py or SQL manually)")
    print("2. Add MCP server to Claude Desktop config (see MCP_README.md)")
    print("3. Restart Claude Desktop")
    print("4. Test by asking Claude to store a conversation")

except Exception as e:
    print(f"\n[ERROR] Validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
