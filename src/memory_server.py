#!/usr/bin/env python3

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server


# Data classes for the knowledge graph
@dataclass
class Entity:
    name: str
    entityType: str
    observations: List[str]
    weight: int = 0


@dataclass 
class Relation:
    from_entity: str  # renamed from 'from' (Python keyword)
    to_entity: str    # renamed from 'to' (Python keyword) 
    relationType: str


@dataclass
class KnowledgeGraph:
    entities: List[Entity]
    relations: List[Relation]


class KnowledgeGraphManager:
    def __init__(self, memory_file_path: str):
        self.memory_file_path = Path(memory_file_path)
    
    def load_graph(self) -> KnowledgeGraph:
        """Load knowledge graph from JSONL file"""
        entities = []
        relations = []
        
        if not self.memory_file_path.exists():
            return KnowledgeGraph(entities=[], relations=[])
        
        try:
            with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    item = json.loads(line)
                    if item.get('type') == 'entity':
                        entity = Entity(
                            name=item['name'],
                            entityType=item['entityType'],
                            observations=item['observations'],
                            weight=item.get('weight', 0)  # Default to 0 for backward compatibility
                        )
                        entities.append(entity)
                    elif item.get('type') == 'relation':
                        relation = Relation(
                            from_entity=item['from_entity'],
                            to_entity=item['to_entity'],
                            relationType=item['relationType']
                        )
                        relations.append(relation)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load memory file: {e}")
            return KnowledgeGraph(entities=[], relations=[])
        
        return KnowledgeGraph(entities=entities, relations=relations)
    
    def save_graph(self, graph: KnowledgeGraph) -> None:
        """Save knowledge graph to JSONL file"""
        # Create directory if it doesn't exist
        self.memory_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.memory_file_path, 'w', encoding='utf-8') as f:
            # Write entities
            for entity in graph.entities:
                entity_dict = asdict(entity)
                entity_dict['type'] = 'entity'
                f.write(json.dumps(entity_dict) + '\n')
            
            # Write relations
            for relation in graph.relations:
                relation_dict = asdict(relation)
                relation_dict['type'] = 'relation'
                f.write(json.dumps(relation_dict) + '\n')
    
    # Entity Operations
    def create_entities(self, entities: List[Entity]) -> None:
        """Create new entities, ignore duplicates"""
        graph = self.load_graph()
        existing_names = {entity.name for entity in graph.entities}
        
        for entity in entities:
            if entity.name not in existing_names:
                graph.entities.append(entity)
                existing_names.add(entity.name)
        
        self.save_graph(graph)
    
    def delete_entities(self, entity_names: List[str]) -> None:
        """Remove entities and cascade delete relations"""
        graph = self.load_graph()
        
        # Remove entities
        graph.entities = [e for e in graph.entities if e.name not in entity_names]
        
        # Remove relations that reference deleted entities
        graph.relations = [
            r for r in graph.relations 
            if r.from_entity not in entity_names and r.to_entity not in entity_names
        ]
        
        self.save_graph(graph)
    
    def add_observations(self, observations: List[dict]) -> None:
        """Add new observations to existing entities"""
        graph = self.load_graph()
        entity_map = {entity.name: entity for entity in graph.entities}
        
        for obs in observations:
            entity_name = obs.get('entityName')
            observation = obs.get('observation')
            
            if entity_name in entity_map and observation:
                if observation not in entity_map[entity_name].observations:
                    entity_map[entity_name].observations.append(observation)
        
        self.save_graph(graph)
    
    def delete_observations(self, deletions: List[dict]) -> None:
        """Remove specific observations from entities"""
        graph = self.load_graph()
        entity_map = {entity.name: entity for entity in graph.entities}
        
        for deletion in deletions:
            entity_name = deletion.get('entityName')
            observation = deletion.get('observation')
            
            if entity_name in entity_map and observation:
                try:
                    entity_map[entity_name].observations.remove(observation)
                except ValueError:
                    pass  # Observation not found, ignore
        
        self.save_graph(graph)
    
    # Relation Operations
    def create_relations(self, relations: List[Relation]) -> None:
        """Create new relations, ignore duplicates"""
        graph = self.load_graph()
        existing_relations = {
            (r.from_entity, r.to_entity, r.relationType) for r in graph.relations
        }
        
        for relation in relations:
            relation_key = (relation.from_entity, relation.to_entity, relation.relationType)
            if relation_key not in existing_relations:
                graph.relations.append(relation)
                existing_relations.add(relation_key)
        
        self.save_graph(graph)
    
    def delete_relations(self, relations: List[dict]) -> None:
        """Remove specific relations"""
        graph = self.load_graph()
        
        # Create set of relations to delete for efficient lookup
        relations_to_delete = {
            (r.get('from_entity'), r.get('to_entity'), r.get('relationType'))
            for r in relations
        }
        
        # Filter out matching relations
        graph.relations = [
            r for r in graph.relations
            if (r.from_entity, r.to_entity, r.relationType) not in relations_to_delete
        ]
        
        self.save_graph(graph)
    
    # Graph Operations
    def read_graph(self) -> KnowledgeGraph:
        """Return entire graph"""
        return self.load_graph()
    
    def search_nodes(self, query: str) -> List[Entity]:
        """Search entities by name/type/observations + increment weights"""
        graph = self.load_graph()
        query_lower = query.lower()
        matching_entities = []
        
        for entity in graph.entities:
            # Search in name, type, and observations
            if (query_lower in entity.name.lower() or 
                query_lower in entity.entityType.lower() or
                any(query_lower in obs.lower() for obs in entity.observations)):
                
                # Increment weight for accessed entity
                entity.weight += 1
                matching_entities.append(entity)
        
        # Save updated weights
        if matching_entities:
            self.save_graph(graph)
        
        return matching_entities
    
    def open_nodes(self, names: List[str]) -> List[Entity]:
        """Get specific entities + increment weights"""
        graph = self.load_graph()
        entity_map = {entity.name: entity for entity in graph.entities}
        found_entities = []
        
        for name in names:
            if name in entity_map:
                entity = entity_map[name]
                entity.weight += 1
                found_entities.append(entity)
        
        # Save updated weights
        if found_entities:
            self.save_graph(graph)
        
        return found_entities
    
    # New Operations
    def prune_entities(self, threshold: int) -> List[str]:
        """Remove entities with weight < threshold"""
        graph = self.load_graph()
        
        # Find entities to prune
        entities_to_prune = [
            entity.name for entity in graph.entities 
            if entity.weight < threshold
        ]
        
        if entities_to_prune:
            # Remove low-weight entities and their relations
            self.delete_entities(entities_to_prune)
        
        return entities_to_prune
    
    def increment_weights(self, entity_names: List[str]) -> None:
        """Increment weight for specified entities"""
        graph = self.load_graph()
        entity_map = {entity.name: entity for entity in graph.entities}
        
        updated = False
        for name in entity_names:
            if name in entity_map:
                entity_map[name].weight += 1
                updated = True
        
        if updated:
            self.save_graph(graph)


# Initialize the knowledge graph manager
MEMORY_FILE_PATH = os.getenv('MEMORY_FILE_PATH', 'memory.jsonl')
knowledge_graph_manager = KnowledgeGraphManager(MEMORY_FILE_PATH)


async def review_conversation_analysis(conversation: str, manager=None) -> dict:
    """
    Analyze conversation text to extract entities, relations, and observations.
    This is a simplified implementation that uses pattern matching for key extraction.
    """
    try:
        # Use provided manager or default global one
        if manager is None:
            manager = knowledge_graph_manager
        
        # Simple analysis using basic text processing
        # In a real implementation, this would use more sophisticated NLP
        
        lines = conversation.split('\n')
        entities_created = []
        relations_created = []
        observations_added = []
        entities_mentioned = set()
        
        # Basic pattern matching for common entity types
        import re
        
        # Look for person names (capitalized words)
        person_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        # Look for locations
        location_keywords = ['office', 'building', 'city', 'street', 'room', 'floor']
        # Look for companies/organizations 
        org_keywords = ['company', 'corporation', 'inc', 'ltd', 'organization', 'team', 'department']
        # Look for concepts/topics
        concept_keywords = ['project', 'meeting', 'task', 'goal', 'plan', 'idea', 'problem']
        
        conversation_lower = conversation.lower()
        
        # Extract potential entities
        extracted_entities = []
        
        # Find person names
        person_matches = re.findall(person_pattern, conversation)
        for person in person_matches[:10]:  # Limit to avoid overwhelming
            if len(person.split()) == 2:  # Simple first+last name check
                extracted_entities.append({
                    'name': person.strip(),
                    'type': 'person',
                    'observations': [f'mentioned in conversation']
                })
                entities_mentioned.add(person.strip())
        
        # Find locations
        for keyword in location_keywords:
            if keyword in conversation_lower:
                # Extract context around the keyword
                for line in lines:
                    if keyword in line.lower():
                        words = line.split()
                        for i, word in enumerate(words):
                            if keyword in word.lower():
                                # Try to extract the full location name
                                context = ' '.join(words[max(0, i-2):i+3])
                                location_name = f"{keyword} from conversation"
                                extracted_entities.append({
                                    'name': location_name,
                                    'type': 'location',
                                    'observations': [context.strip()[:100]]
                                })
                                entities_mentioned.add(location_name)
                                break
                        break
        
        # Find organizations
        for keyword in org_keywords:
            if keyword in conversation_lower:
                for line in lines:
                    if keyword in line.lower():
                        words = line.split()
                        for i, word in enumerate(words):  
                            if keyword in word.lower():
                                context = ' '.join(words[max(0, i-2):i+3])
                                org_name = f"{keyword} from conversation"
                                extracted_entities.append({
                                    'name': org_name,
                                    'type': 'organization', 
                                    'observations': [context.strip()[:100]]
                                })
                                entities_mentioned.add(org_name)
                                break
                        break
        
        # Find concepts
        for keyword in concept_keywords:
            if keyword in conversation_lower:
                for line in lines:
                    if keyword in line.lower():
                        words = line.split()
                        for i, word in enumerate(words):
                            if keyword in word.lower():
                                context = ' '.join(words[max(0, i-2):i+3])
                                concept_name = f"{keyword} from conversation"
                                extracted_entities.append({
                                    'name': concept_name,
                                    'type': 'concept',
                                    'observations': [context.strip()[:100]]
                                })
                                entities_mentioned.add(concept_name)
                                break
                        break
        
        # Create unique entities (avoid duplicates)
        unique_entities = []
        seen_names = set()
        for entity in extracted_entities:
            if entity['name'] not in seen_names:
                unique_entities.append(entity)
                seen_names.add(entity['name'])
        
        # Convert to Entity objects and create them
        entity_objects = []
        for entity_data in unique_entities:
            entity = Entity(
                name=entity_data['name'],
                entityType=entity_data['type'],
                observations=entity_data['observations'],
                weight=1  # Start with weight 1 for new entities
            )
            entity_objects.append(entity)
        
        if entity_objects:
            manager.create_entities(entity_objects)
            entities_created = [entity.name for entity in entity_objects]
        
        # Create some basic relations if we have multiple entities
        if len(entity_objects) >= 2:
            relations = []
            # Create "mentioned_with" relations between entities found in the same conversation
            for i, entity1 in enumerate(entity_objects):
                for entity2 in entity_objects[i+1:]:
                    if entity1.entityType != entity2.entityType:  # Don't relate same types
                        relation = Relation(
                            from_entity=entity1.name,
                            to_entity=entity2.name,
                            relationType="mentioned_with"
                        )
                        relations.append(relation)
            
            if relations:
                manager.create_relations(relations[:5])  # Limit relations
                relations_created = [(r.from_entity, r.to_entity, r.relationType) for r in relations[:5]]
        
        # Increment weights for all mentioned entities (existing ones)
        if entities_mentioned:
            existing_entity_names = list(entities_mentioned)
            manager.increment_weights(existing_entity_names)
        
        return {
            "success": True,
            "entities_created": entities_created,
            "relations_created": relations_created,
            "observations_added": observations_added,
            "entities_mentioned": list(entities_mentioned),
            "summary": f"Extracted {len(entities_created)} entities, {len(relations_created)} relations, and incremented weights for {len(entities_mentioned)} mentioned entities"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversation analysis failed: {str(e)}"
        }


# MCP Server setup
app = Server("memory-server")

# Tool handlers using the official MCP SDK pattern
@app.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> list:
    """Handle tool calls from MCP clients"""
    
    if name == "create_entities":
        try:
            entities_data = arguments.get("entities", [])
            entity_objects = []
            for entity_data in entities_data:
                entity = Entity(
                    name=entity_data['name'],
                    entityType=entity_data['entityType'],
                    observations=entity_data.get('observations', []),
                    weight=entity_data.get('weight', 0)
                )
                entity_objects.append(entity)
            
            knowledge_graph_manager.create_entities(entity_objects)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Created {len(entity_objects)} entities"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "create_relations":
        try:
            relations_data = arguments.get("relations", [])
            relation_objects = []
            for relation_data in relations_data:
                relation = Relation(
                    from_entity=relation_data['from_entity'],
                    to_entity=relation_data['to_entity'],
                    relationType=relation_data['relationType']
                )
                relation_objects.append(relation)
            
            knowledge_graph_manager.create_relations(relation_objects)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Created {len(relation_objects)} relations"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "add_observations":
        try:
            observations = arguments.get("observations", [])
            knowledge_graph_manager.add_observations(observations)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Added {len(observations)} observations"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "delete_entities":
        try:
            entity_names = arguments.get("entity_names", [])
            knowledge_graph_manager.delete_entities(entity_names)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Deleted {len(entity_names)} entities"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "delete_observations":
        try:
            deletions = arguments.get("deletions", [])
            knowledge_graph_manager.delete_observations(deletions)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Deleted {len(deletions)} observations"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "delete_relations":
        try:
            relations = arguments.get("relations", [])
            knowledge_graph_manager.delete_relations(relations)
            return [{"type": "text", "text": json.dumps({"success": True, "message": f"Deleted {len(relations)} relations"})}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "read_graph":
        try:
            graph = knowledge_graph_manager.read_graph()
            graph_dict = {
                "entities": [asdict(entity) for entity in graph.entities],
                "relations": [asdict(relation) for relation in graph.relations]
            }
            return [{"type": "text", "text": json.dumps(graph_dict)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "search_nodes":
        try:
            query = arguments.get("query", "")
            entities = knowledge_graph_manager.search_nodes(query)
            entities_dict = [asdict(entity) for entity in entities]
            result = {
                "success": True,
                "entities": entities_dict,
                "count": len(entities)
            }
            return [{"type": "text", "text": json.dumps(result)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "open_nodes":
        try:
            names = arguments.get("names", [])
            entities = knowledge_graph_manager.open_nodes(names)
            entities_dict = [asdict(entity) for entity in entities]
            result = {
                "success": True,
                "entities": entities_dict,
                "count": len(entities)
            }
            return [{"type": "text", "text": json.dumps(result)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "prune_entities":
        try:
            threshold = arguments.get("threshold", 0)
            pruned_names = knowledge_graph_manager.prune_entities(threshold)
            result = {
                "success": True,
                "pruned_entities": pruned_names,
                "count": len(pruned_names),
                "message": f"Pruned {len(pruned_names)} entities with weight < {threshold}"
            }
            return [{"type": "text", "text": json.dumps(result)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    elif name == "review_conversation":
        try:
            conversation = arguments.get("conversation", "")
            result = await review_conversation_analysis(conversation)
            return [{"type": "text", "text": json.dumps(result)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"success": False, "error": str(e)})}]
    
    else:
        return [{"type": "text", "text": json.dumps({"success": False, "error": f"Unknown tool: {name}"})}]


@app.list_tools()
async def list_tools() -> list:
    """List available tools for MCP clients"""
    return [
        {
            "name": "create_entities",
            "description": "Create multiple entities in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "entityType": {"type": "string"},
                                "observations": {"type": "array", "items": {"type": "string"}},
                                "weight": {"type": "integer", "default": 0}
                            },
                            "required": ["name", "entityType"]
                        }
                    }
                },
                "required": ["entities"]
            }
        },
        {
            "name": "create_relations",
            "description": "Create multiple relations in the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_entity": {"type": "string"},
                                "to_entity": {"type": "string"},
                                "relationType": {"type": "string"}
                            },
                            "required": ["from_entity", "to_entity", "relationType"]
                        }
                    }
                },
                "required": ["relations"]
            }
        },
        {
            "name": "add_observations",
            "description": "Add observations to existing entities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string"},
                                "observation": {"type": "string"}
                            },
                            "required": ["entityName", "observation"]
                        }
                    }
                },
                "required": ["observations"]
            }
        },
        {
            "name": "delete_entities",
            "description": "Delete entities and cascade delete their relations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entity_names": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["entity_names"]
            }
        },
        {
            "name": "delete_observations",
            "description": "Remove specific observations from entities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "deletions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {"type": "string"},
                                "observation": {"type": "string"}
                            },
                            "required": ["entityName", "observation"]
                        }
                    }
                },
                "required": ["deletions"]
            }
        },
        {
            "name": "delete_relations",
            "description": "Remove specific relations from the knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_entity": {"type": "string"},
                                "to_entity": {"type": "string"},
                                "relationType": {"type": "string"}
                            },
                            "required": ["from_entity", "to_entity", "relationType"]
                        }
                    }
                },
                "required": ["relations"]
            }
        },
        {
            "name": "read_graph",
            "description": "Get the entire knowledge graph",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "search_nodes",
            "description": "Search entities by name/type/observations and increment their weights",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "open_nodes",
            "description": "Get specific entities by name and increment their weights",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["names"]
            }
        },
        {
            "name": "prune_entities",
            "description": "Remove entities with weight below threshold and their relations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "description": "Minimum weight threshold - entities below this will be removed"
                    }
                },
                "required": ["threshold"]
            }
        },
        {
            "name": "review_conversation",
            "description": "Analyze conversation text to extract and store entities, relations, and observations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "conversation": {
                        "type": "string",
                        "description": "Full conversation text to analyze for knowledge extraction"
                    }
                },
                "required": ["conversation"]
            }
        }
    ]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
