# Claude Desktop Integration Guide

## Step-by-Step Setup Instructions

### Step 1: Verify Python Environment
First, ensure Python 3.8+ is installed and accessible from the command line:
```bash
python --version
```

### Step 2: Install Dependencies
The MCP package should already be available. Test it:
```bash
cd C:\Users\steve\claude\memory\src
python -c "from mcp.server import Server; print('MCP available')"
```

### Step 3: Test the Memory Server
Test the server can start properly:
```bash
cd C:\Users\steve\claude\memory\src
python memory_server.py
```
Press Ctrl+C to stop the test.

### Step 4: Configure Claude Desktop
You need to add the memory server configuration to Claude Desktop's settings.

#### For Windows:
1. Open Claude Desktop
2. Go to Settings (gear icon)
3. Navigate to the "Developer" or "MCP Servers" section
4. Add a new server configuration

#### Configuration JSON:
Add this configuration to Claude Desktop:

```json
{
  "name": "memory-server",
  "command": "python",
  "args": ["C:\\Users\\steve\\claude\\memory\\src\\memory_server.py"],
  "env": {
    "MEMORY_FILE_PATH": "C:\\Users\\steve\\claude\\memory\\memory.jsonl"
  }
}
```

### Step 5: Alternative - Create Batch File (Recommended)
For easier configuration, create a batch file:

1. Create `start_memory_server.bat` in `C:\Users\steve\claude\memory\`
2. Add the batch file path to Claude Desktop instead

### Step 6: Restart Claude Desktop
After adding the configuration:
1. Close Claude Desktop completely
2. Restart Claude Desktop
3. The memory server should now be available

### Step 7: Verify Integration
In Claude Desktop, you should now be able to use memory commands like:
- "Search for entities about..."
- "Create a new entity..."
- "Review this conversation for entities..."

## Troubleshooting

### Common Issues:
1. **Python not found**: Ensure Python is in your system PATH
2. **Module not found**: Verify MCP package is installed
3. **Server won't start**: Check the memory_server.py file path
4. **Claude can't connect**: Verify the configuration JSON is correct

### Debug Steps:
1. Test server manually: `python memory_server.py`
2. Check Claude Desktop logs/console for errors
3. Verify file paths are correct (use absolute paths)
4. Ensure memory.jsonl file location is accessible

## Available Tools
Once integrated, these 11 tools will be available:
1. create_entities
2. create_relations  
3. add_observations
4. delete_entities
5. delete_observations
6. delete_relations
7. read_graph
8. search_nodes
9. open_nodes
10. prune_entities
11. review_conversation
