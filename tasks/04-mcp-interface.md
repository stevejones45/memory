# MCP Tool Interface

## Existing Tools (Direct Port)
1. **create_entities** - Create multiple entities
2. **create_relations** - Create multiple relations  
3. **add_observations** - Add observations to entities
4. **delete_entities** - Remove entities and relations
5. **delete_observations** - Remove specific observations
6. **delete_relations** - Remove specific relations
7. **read_graph** - Get entire knowledge graph
8. **search_nodes** - Search with query + increment weights
9. **open_nodes** - Get specific nodes + increment weights

## New Tools - ✅ COMPLETED
10. **prune_entities** ✅
    - Input: `threshold` (int)
    - Action: Remove entities with weight < threshold
    - Output: List of pruned entity names and count
    - Status: Implemented with cascade deletion for relations

11. **review_conversation** ✅
    - Input: `conversation` (string) - entire conversation text
    - Action: LLM analyzes conversation for key insights
    - Extracts entities, relations, observations using pattern matching
    - Increments weights for mentioned entities
    - Output: Summary of what was saved/updated
    - Status: Implemented with intelligent text processing

## Tool Schema Structure
- Use Python MCP SDK tool registration
- JSON schema validation for inputs
- Consistent return format (JSON strings)

## Weight Increment Integration
- `search_nodes` and `open_nodes` automatically increment weights
- `review_conversation` increments weights for mentioned entities
- All other tools leave weights unchanged
