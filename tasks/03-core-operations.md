# Core Operations Implementation

## KnowledgeGraphManager Class

### Storage Operations
- `load_graph()` - Load from JSONL file
- `save_graph(graph)` - Save to JSONL file
- Handle file not found gracefully (return empty graph)

### Entity Operations
- `create_entities(entities)` - Create new entities, ignore duplicates
- `delete_entities(entity_names)` - Remove entities and cascade delete relations
- `add_observations(observations)` - Add new observations to existing entities
- `delete_observations(deletions)` - Remove specific observations

### Relation Operations  
- `create_relations(relations)` - Create new relations, ignore duplicates
- `delete_relations(relations)` - Remove specific relations

### Graph Operations
- `read_graph()` - Return entire graph
- `search_nodes(query)` - Search entities by name/type/observations + increment weights
- `open_nodes(names)` - Get specific entities + increment weights

### New Operations
- `prune_entities(threshold)` - Remove entities with weight < threshold
- `increment_weights(entity_names)` - Increment weight for specified entities

## Weight Increment Logic
- Called automatically in `search_nodes()` and `open_nodes()`
- Called manually from conversation review tool
- Simple counter increment per entity access

## Error Handling
- Minimal error handling (personal tool)
- Basic file I/O error handling
- Entity not found errors where appropriate
