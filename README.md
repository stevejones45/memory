# Memory System - Claude Desktop Integration

A comprehensive knowledge graph memory system for Claude Desktop using MCP (Model Context Protocol).

## Features

- **11 MCP Tools** for complete knowledge management
- **Weight-based Entity Management** with automatic importance tracking
- **Conversation Analysis** with intelligent entity extraction
- **JSONL Storage** for reliable data persistence
- **Pruning System** for memory optimization

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Claude Desktop application
- MCP support enabled in Claude Desktop

### Installation Steps

#### 1. Verify the Installation
The memory system is already set up at `C:\Users\steve\claude\memory\`. Verify it works:

```bash
cd C:\Users\steve\claude\memory\src
python memory_server.py
```

Press Ctrl+C to stop the test. If no errors appear, the server is ready.

#### 2. Configure Claude Desktop

**Option A: Direct Configuration (Recommended)**
1. Open Claude Desktop
2. Go to Settings → Developer → MCP Servers
3. Add new server with these settings:
   - **Name**: `memory-server`
   - **Command**: `python`
   - **Arguments**: `C:\Users\steve\claude\memory\src\memory_server.py`
   - **Environment Variables**: 
     - `MEMORY_FILE_PATH`: `C:\Users\steve\claude\memory\memory.jsonl`

**Option B: Using Batch File**
1. Use the provided batch file: `C:\Users\steve\claude\memory\start_memory_server.bat`
2. In Claude Desktop MCP settings:
   - **Name**: `memory-server`
   - **Command**: `C:\Users\steve\claude\memory\start_memory_server.bat`

**Option C: Configuration File**
1. Locate your Claude Desktop configuration directory (usually in AppData)
2. Add the contents of `claude_desktop_config.json` to your Claude Desktop config

#### 3. Restart Claude Desktop
- Close Claude Desktop completely
- Restart the application
- The memory tools should now be available

### Verification

Once integrated, test with these commands in Claude Desktop:

```
Create a new entity named "Test Entity" of type "concept" with observation "This is a test"
```

```
Search for entities containing "test"
```

```
Review this conversation for any entities or relationships
```

## Available Tools

### Core Entity Management
- **create_entities** - Create new entities with observations
- **delete_entities** - Remove entities and their relations
- **add_observations** - Add new observations to existing entities
- **delete_observations** - Remove specific observations

### Relationship Management  
- **create_relations** - Create relationships between entities
- **delete_relations** - Remove specific relationships

### Knowledge Graph Operations
- **read_graph** - Get the complete knowledge graph
- **search_nodes** - Search entities by name/type/observations (increments weights)
- **open_nodes** - Retrieve specific entities by name (increments weights)

### Advanced Features
- **prune_entities** - Remove low-weight entities below threshold
- **review_conversation** - Analyze conversation text for entities and relationships

## Usage Examples

### Basic Entity Creation
```
Create entities for:
- Name: "John Doe", Type: "person", Observations: ["Software engineer", "Python expert"]
- Name: "TechCorp", Type: "organization", Observations: ["Software company"]
```

### Relationship Creation
```
Create a relationship from "John Doe" to "TechCorp" with type "works_at"
```

### Conversation Analysis
```
Review this conversation: "I spoke with Sarah about the new project. She mentioned that the team is working on a machine learning system for customer analytics."
```

### Memory Management
```
Prune entities with weight less than 2 to clean up unused data
```

## Data Storage

- **Location**: `C:\Users\steve\claude\memory\memory.jsonl`
- **Format**: JSONL (JSON Lines) for efficient streaming
- **Backup**: Consider backing up the .jsonl file regularly

## Weight System

The system automatically tracks entity importance:
- **Search/Open**: Increments weight by 1 when entities are accessed
- **Conversation**: New entities start with weight 1, existing get incremented
- **Pruning**: Remove entities below specified weight threshold

## Troubleshooting

### Server Won't Start
1. Verify Python is installed: `python --version`
2. Check file paths are correct
3. Ensure no other process is using the same port

### Claude Desktop Can't Connect
1. Verify MCP server configuration is correct
2. Check Claude Desktop logs for errors
3. Restart Claude Desktop after configuration changes
4. Ensure server starts without errors when run manually

### Memory File Issues
1. Check file permissions on the memory.jsonl location
2. Verify the directory exists and is writable
3. Check disk space availability

### Performance Issues
- Use `prune_entities` regularly to remove unused entities
- Monitor memory.jsonl file size
- Consider archiving old data if file becomes very large

## Development

### Testing
- Run integration tests: `python test_phase5.py`
- Run individual phase tests: `python test_phase1.py` through `python test_phase4.py`

### Customization
- Modify `memory_server.py` for custom functionality
- Adjust conversation analysis patterns in `review_conversation_analysis()`
- Configure weight increment values and pruning thresholds

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test files for usage examples
3. Examine the source code in `src/memory_server.py`
4. Check Claude Desktop documentation for MCP server configuration

## License

This memory system is designed for use with Claude Desktop and follows MCP protocol standards.
