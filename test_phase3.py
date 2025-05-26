#!/usr/bin/env python3

import json
import os
import asyncio
from pathlib import Path

# Add src to path so we can import our modules
import sys
sys.path.append(str(Path(__file__).parent / 'src'))

from memory_server import knowledge_graph_manager, Entity, Relation

def test_phase3():
    """Test Phase 3: MCP Tool Integration"""
    print("Testing Phase 3: MCP Tool Integration")
    print("=" * 50)
    
    # Clean up any existing test file
    test_file = Path('test_phase3_memory.jsonl')
    if test_file.exists():
        test_file.unlink()
    
    # Create a test knowledge graph manager
    test_manager = knowledge_graph_manager.__class__('test_phase3_memory.jsonl')
    
    # Test data
    entities_data = [
        {
            "name": "Alice",
            "entityType": "person",
            "observations": ["works at Tech Corp", "likes coffee"],
            "weight": 5
        },
        {
            "name": "Bob", 
            "entityType": "person",
            "observations": ["manager at Tech Corp"],
            "weight": 3
        }
    ]
    
    relations_data = [
        {
            "from_entity": "Alice",
            "to_entity": "Bob", 
            "relationType": "reports_to"
        }
    ]
    
    # Test 1: Create entities
    print("1. Testing create_entities functionality...", end="")
    entity_objects = []
    for entity_data in entities_data:
        entity = Entity(
            name=entity_data['name'],
            entityType=entity_data['entityType'],
            observations=entity_data.get('observations', []),
            weight=entity_data.get('weight', 0)
        )
        entity_objects.append(entity)
    
    test_manager.create_entities(entity_objects)
    graph = test_manager.read_graph()
    assert len(graph.entities) == 2
    assert graph.entities[0].name == "Alice"
    assert graph.entities[0].weight == 5
    print("PASS")
    
    # Test 2: Create relations
    print("2. Testing create_relations functionality...", end="")
    relation_objects = []
    for relation_data in relations_data:
        relation = Relation(
            from_entity=relation_data['from_entity'],
            to_entity=relation_data['to_entity'],
            relationType=relation_data['relationType']
        )
        relation_objects.append(relation)
    
    test_manager.create_relations(relation_objects)
    graph = test_manager.read_graph()
    assert len(graph.relations) == 1
    assert graph.relations[0].from_entity == "Alice"
    print("PASS")
    
    # Test 3: Search nodes (with weight increment)
    print("3. Testing search_nodes functionality...", end="")
    initial_weight = graph.entities[0].weight  # Alice's weight
    results = test_manager.search_nodes("coffee")
    assert len(results) == 1
    assert results[0].name == "Alice"
    # Check weight was incremented
    updated_graph = test_manager.read_graph()
    alice_entity = next(e for e in updated_graph.entities if e.name == "Alice")
    assert alice_entity.weight == initial_weight + 1
    print("PASS")
    
    # Test 4: Open nodes (with weight increment)
    print("4. Testing open_nodes functionality...", end="")
    current_weight = alice_entity.weight
    results = test_manager.open_nodes(["Alice", "Bob"])
    assert len(results) == 2
    # Check weights were incremented
    updated_graph = test_manager.read_graph()
    alice_entity = next(e for e in updated_graph.entities if e.name == "Alice")
    bob_entity = next(e for e in updated_graph.entities if e.name == "Bob")
    assert alice_entity.weight == current_weight + 1
    assert bob_entity.weight == 4  # was 3, now 4
    print("PASS")
    
    # Test 5: Add observations
    print("5. Testing add_observations functionality...", end="")
    observations = [
        {"entityName": "Alice", "observation": "enjoys hiking"},
        {"entityName": "Bob", "observation": "plays guitar"}
    ]
    test_manager.add_observations(observations)
    graph = test_manager.read_graph()
    alice_entity = next(e for e in graph.entities if e.name == "Alice")
    bob_entity = next(e for e in graph.entities if e.name == "Bob")
    assert "enjoys hiking" in alice_entity.observations
    assert "plays guitar" in bob_entity.observations
    print("PASS")
    
    # Test 6: Delete observations
    print("6. Testing delete_observations functionality...", end="")
    deletions = [{"entityName": "Alice", "observation": "enjoys hiking"}]
    test_manager.delete_observations(deletions)
    graph = test_manager.read_graph()
    alice_entity = next(e for e in graph.entities if e.name == "Alice")
    assert "enjoys hiking" not in alice_entity.observations
    print("PASS")
    
    # Test 7: Delete relations
    print("7. Testing delete_relations functionality...", end="")
    relations_to_delete = [
        {
            "from_entity": "Alice",
            "to_entity": "Bob",
            "relationType": "reports_to"
        }
    ]
    test_manager.delete_relations(relations_to_delete)
    graph = test_manager.read_graph()
    assert len(graph.relations) == 0
    print("PASS")
    
    # Test 8: Delete entities (cascade)
    print("8. Testing delete_entities functionality...", end="")
    # First add back a relation to test cascade
    test_manager.create_relations(relation_objects)
    graph = test_manager.read_graph()
    assert len(graph.relations) == 1  # Relation exists
    
    # Now delete Alice, should cascade delete the relation
    test_manager.delete_entities(["Alice"])
    graph = test_manager.read_graph()
    assert len(graph.entities) == 1  # Only Bob remains
    assert graph.entities[0].name == "Bob"
    assert len(graph.relations) == 0  # Relation was cascade deleted
    print("PASS")
    
    # Test 9: Read graph (JSON serialization test)
    print("9. Testing read_graph JSON serialization...", end="")
    graph = test_manager.read_graph()
    # Test that we can convert to dict format like the MCP tool would
    graph_dict = {
        "entities": [
            {
                "name": entity.name,
                "entityType": entity.entityType,
                "observations": entity.observations,
                "weight": entity.weight
            } for entity in graph.entities
        ],
        "relations": [
            {
                "from_entity": relation.from_entity,
                "to_entity": relation.to_entity,
                "relationType": relation.relationType
            } for relation in graph.relations
        ]
    }
    json_output = json.dumps(graph_dict)
    parsed_back = json.loads(json_output)
    assert len(parsed_back["entities"]) == 1
    assert parsed_back["entities"][0]["name"] == "Bob"
    print("PASS")
    
    # Clean up test file
    if test_file.exists():
        test_file.unlink()
    
    print("\nSUCCESS: All Phase 3 functionality tests passed!")
    print("MCP tools are ready for integration testing.")

if __name__ == "__main__":
    test_phase3()
