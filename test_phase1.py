#!/usr/bin/env python3
"""
Simple test script for Phase 1 - Basic Structure
Tests the data classes and JSONL storage operations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from memory_server import KnowledgeGraphManager, Entity, Relation, KnowledgeGraph

def test_basic_operations():
    """Test basic file operations"""
    print("Testing Phase 1: Basic Structure")
    print("=" * 40)
    
    # Test with test data file
    test_file = "test_data.jsonl"
    manager = KnowledgeGraphManager(test_file)
    
    # Test loading
    print("1. Testing load_graph()...")
    graph = manager.load_graph()
    print(f"   Loaded {len(graph.entities)} entities, {len(graph.relations)} relations")
    
    for entity in graph.entities:
        print(f"   Entity: {entity.name} (type: {entity.entityType}, weight: {entity.weight})")
        print(f"     Observations: {entity.observations}")
    
    for relation in graph.relations:
        print(f"   Relation: {relation.from_entity} -> {relation.to_entity} ({relation.relationType})")
    
    print()
    
    # Test creating new data
    print("2. Testing data creation...")
    new_entity = Entity(
        name="Claude",
        entityType="AI",
        observations=["helpful assistant", "created by Anthropic"],
        weight=1
    )
    
    new_relation = Relation(
        from_entity="test_user",
        to_entity="Claude",
        relationType="interacts_with"
    )
    
    # Add to graph
    graph.entities.append(new_entity)
    graph.relations.append(new_relation)
    
    print(f"   Added entity: {new_entity.name}")
    print(f"   Added relation: {new_relation.from_entity} -> {new_relation.to_entity}")
    print()
    
    # Test saving
    print("3. Testing save_graph()...")
    test_output = "test_output.jsonl"
    output_manager = KnowledgeGraphManager(test_output)
    output_manager.save_graph(graph)
    print(f"   Saved graph to {test_output}")
    
    # Test loading the saved file
    print("4. Testing reload of saved data...")
    reloaded_graph = output_manager.load_graph()
    print(f"   Reloaded {len(reloaded_graph.entities)} entities, {len(reloaded_graph.relations)} relations")
    
    # Verify data integrity
    print("5. Verifying data integrity...")
    assert len(reloaded_graph.entities) == len(graph.entities), "Entity count mismatch"
    assert len(reloaded_graph.relations) == len(graph.relations), "Relation count mismatch"
    
    # Check specific entity
    claude_entity = next((e for e in reloaded_graph.entities if e.name == "Claude"), None)
    assert claude_entity is not None, "Claude entity not found"
    assert claude_entity.weight == 1, "Weight not preserved"
    assert "helpful assistant" in claude_entity.observations, "Observations not preserved"
    
    print("   [OK] All data integrity checks passed")
    print()
    
    # Test non-existent file
    print("6. Testing non-existent file handling...")
    nonexistent_manager = KnowledgeGraphManager("nonexistent.jsonl")
    empty_graph = nonexistent_manager.load_graph()
    print(f"   Empty graph created: {len(empty_graph.entities)} entities, {len(empty_graph.relations)} relations")
    assert len(empty_graph.entities) == 0, "Should have empty entities"
    assert len(empty_graph.relations) == 0, "Should have empty relations"
    print("   [OK] Non-existent file handled correctly")
    
    print()
    print("Phase 1 Complete: All basic operations working correctly!")
    print("[OK] Data classes created")
    print("[OK] JSONL storage implemented")
    print("[OK] Load/save operations working")
    print("[OK] Weight system integrated")
    print("[OK] Error handling for missing files")

if __name__ == "__main__":
    test_basic_operations()
