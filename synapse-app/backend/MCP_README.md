# Synapse MCP Server

Store AI chat conversations from any app into your Synapse second brain.

## What is this?

The Synapse MCP (Model Context Protocol) server allows AI assistants like Claude Desktop, ChatGPT, and others to store conversations directly into your Synapse database.

**Use cases:**
- Archive important AI conversations for later search
- Build a searchable knowledge base from all your AI chats
- Keep records of research, code discussions, brainstorming sessions
- Semantic search across all your AI conversations

## How it works

1. **Client provides**: Full conversation text + summary + metadata
2. **MCP server**: Generates embeddings and stores in Qdrant + Supabase
3. **You can**: Search and retrieve conversations later in Synapse

## Setup

### 1. Create Supabase Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Run the migration
\i migrations/create_chat_records_table.sql
```

Or copy the SQL from `migrations/create_chat_records_table.sql` and run it manually.

### 2. Configure Claude Desktop (or other MCP client)

Add to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "synapse-chat-storage": {
      "command": "python",
      "args": [
        "E:\\Appointy_Task_1\\synapse-app\\backend\\mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "E:\\Appointy_Task_1\\synapse-app\\backend"
      }
    }
  }
}
```

**Important**: Update the paths to match your installation directory.

### 3. Restart Claude Desktop

After adding the config, restart Claude Desktop. You should see the Synapse tool available.

## Using the MCP Server

### Tool: `store_chat`

Stores a conversation in Synapse.

**Parameters:**
- `text` (required): Full conversation text to embed and make searchable
- `summary` (required): Short 1-2 sentence summary
- `title` (required): Brief title for the conversation
- `source_app` (optional): Where this chat is from (e.g., "Claude", "ChatGPT")
- `tags` (optional): Array of tags/categories

**Example (in Claude Desktop):**

```
Please store this conversation using the store_chat tool.

Title: "Python Async Best Practices"
Summary: "Discussion about asyncio patterns, event loops, and error handling in Python async code"
Tags: ["python", "async", "programming"]
Source: "Claude Desktop"
```

Claude will automatically call the MCP tool and store the conversation.

## Testing the MCP Server

Run the MCP server directly to test:

```bash
cd E:\Appointy_Task_1\synapse-app\backend
python mcp_server.py
```

You should see:
```
[MCP] Synapse Chat Storage Server starting...
[MCP] This server stores AI chat conversations in Synapse
[MCP] Waiting for client connections...
```

Press Ctrl+C to stop.

## What gets stored?

### In Qdrant (for semantic search):
- Full text embedding (3072 dimensions)
- Metadata: title, summary, source_app, tags, timestamp

### In Supabase (for records):
- Title
- Summary
- Source app
- Tags
- Word count
- First 2000 characters (preview)
- Timestamp

## Searching stored chats

Use the Synapse search API to find stored conversations:

```bash
curl "http://localhost:8000/api/search?q=python+async+patterns"
```

Or use the Synapse Electron app (when built) to browse and search all your chats.

## Troubleshooting

**MCP server not appearing in Claude Desktop:**
- Check the config file path is correct
- Verify Python path is correct
- Restart Claude Desktop completely
- Check Claude Desktop logs

**"Table chat_records does not exist" error:**
- Run the SQL migration in Supabase
- Check your Supabase credentials in `.env`

**Embedding errors:**
- Verify `BASE_URL` and `AUTH_TOKEN` in `.env`
- Check LiteLLM proxy is accessible
- Test with: `curl -H "Authorization: Bearer YOUR_TOKEN" YOUR_BASE_URL/v1/models`

## Architecture

```
AI App (Claude/ChatGPT)
    ↓
MCP Client (sends conversation)
    ↓
Synapse MCP Server
    ↓
    ├→ Generate Embedding (Gemini)
    ├→ Store in Qdrant (semantic search)
    └→ Store in Supabase (records)
```

## Next Steps

- Build Electron app UI to browse chat records
- Add conversation deletion/editing
- Support for conversation threads
- Export conversations to markdown
