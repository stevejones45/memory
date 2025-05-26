# Configuration and Deployment

## File Structure
```
claude/memory/
├── tasks/           # Project planning files
├── src/
│   └── memory_server.py  # Main implementation
├── requirements.txt
├── README.md
└── memory.jsonl     # Data storage file
```

## Environment Variables
- `MEMORY_FILE_PATH` - Path to memory storage file (default: memory.jsonl)

## MCP Configuration
Add to claude_desktop_config.json:
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["C:/Users/steve/claude/memory/src/memory_server.py"],
      "env": {
        "MEMORY_FILE_PATH": "C:/Users/steve/claude/memory/memory.jsonl"
      }
    }
  }
}
```

## Installation
```bash
cd claude/memory
pip install -r requirements.txt
```

## Usage Notes
- Memory file created automatically on first use
- Weight system builds over time with usage
- Conversation review best used periodically
- Pruning removes unused concepts to maintain focus

## System Prompt Integration
Example prompt for using the memory system:
```
You have access to a memory system. Use it to:
1. Remember facts about the user and their interests
2. Build connections between concepts 
3. Periodically review conversations to extract insights
4. Prune unused memories to maintain focus

The weight system tracks conceptual importance - higher weights indicate more central concepts in the user's mental model.
```
