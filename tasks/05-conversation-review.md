# Conversation Review Tool Design

## Purpose
Automatic extraction and storage of conversation insights to build user's conceptual framework.

## Input
- `conversation`: Full conversation text as string
- No specific format required - raw conversation dump

## Process
1. **Analysis Phase**
   - LLM analyzes conversation for salient points
   - Identifies key entities (people, places, concepts, events)
   - Identifies relationships between entities
   - Extracts factual observations about entities

2. **Storage Phase**
   - Create new entities if they don't exist
   - Add new observations to existing entities
   - Create new relations between entities
   - Increment weights for all mentioned entities

3. **Response Phase**
   - Return summary of actions taken
   - List entities created/updated
   - List relations created
   - List observations added

## Implementation Strategy
- Use the LLM itself to do the analysis (no external AI libraries)
- Provide structured prompt for consistent extraction
- Process results into entity/relation/observation structures
- Use existing KnowledgeGraphManager methods for storage

## Example Analysis Prompt
```
Analyze this conversation and extract:
1. Key entities (people, places, concepts, events) with types
2. Important relationships between entities
3. Factual observations about each entity

Return in structured format:
ENTITIES: name|type|observations
RELATIONS: from|to|relationship_type
```

## Weight Increment Logic
- All entities mentioned in conversation get +1 weight
- Builds conceptual density map over time
- Enables identification of important concepts through usage patterns
