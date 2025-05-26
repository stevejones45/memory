#!/usr/bin/env python3

import os
import sys
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from memory_server import KnowledgeGraphManager, Entity, Relation, KnowledgeGraph


def test_phase2():
    """Test all Phase 2 core operations"""
    
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        manager = KnowledgeGraphManager(tmp_path)
        print("Testing Phase 2: Core Operations")
        print("=" * 50)
        
        # Test 1: Create entities
        print("1. Testing create_entities...")
        entities = [
            Entity("Alice", "person", ["works at tech company", "likes coffee"], 0),
            Entity("TechCorp", "company", ["software development", "remote work"], 0),
            Entity("Python", "technology", ["programming language", "popular for AI"], 0)
        ]
        manager.create_entities(entities)
        
        # Test duplicate handling
        manager.create_entities([Entity("Alice", "person", ["duplicate test"], 0)])
        
        graph = manager.read_graph()
        assert len(graph.entities) == 3, f"Expected 3 entities, got {len(graph.entities)}"
        print("   PASS create_entities works correctly")
        
        # Test 2: Create relations
        print("2. Testing create_relations...")
        relations = [
            Relation("Alice", "TechCorp", "works_at"),
            Relation("Alice", "Python", "uses"),
            Relation("TechCorp", "Python", "develops_with")
        ]
        manager.create_relations(relations)
        
        # Test duplicate handling
        manager.create_relations([Relation("Alice", "TechCorp", "works_at")])
        
        graph = manager.read_graph()
        assert len(graph.relations) == 3, f"Expected 3 relations, got {len(graph.relations)}"
        print("   PASS create_relations works correctly")
        
        # Test 3: Add observations
        print("3. Testing add_observations...")
        observations = [
            {"entityName": "Alice", "observation": "drinks tea sometimes"},
            {"entityName": "TechCorp", "observation": "has good benefits"},
            {"entityName": "NonExistent", "observation": "should be ignored"}
        ]
        manager.add_observations(observations)
        
        graph = manager.read_graph()
        alice = next(e for e in graph.entities if e.name == "Alice")
        assert "drinks tea sometimes" in alice.observations
        print("   PASS add_observations works correctly")
        
        # Test 4: Search nodes (with weight increment)
        print("4. Testing search_nodes...")
        initial_graph = manager.read_graph()
        initial_weights = {e.name: e.weight for e in initial_graph.entities}
        
        results = manager.search_nodes("company")  # Should only match TechCorp
        result_names = [r.name for r in results]
        print(f"   Search results: {result_names}")
        
        # Check weight increment only for matched entities
        graph = manager.read_graph()
        for entity in graph.entities:
            expected_weight = initial_weights[entity.name]
            if entity.name in result_names:
                expected_weight += 1
            assert entity.weight == expected_weight, f"{entity.name} weight should be {expected_weight}, got {entity.weight}"
        
        print("   PASS search_nodes with weight increment works correctly")
        
        # Test 5: Open nodes (with weight increment)
        print("5. Testing open_nodes...")
        pre_open_graph = manager.read_graph()
        pre_open_weights = {e.name: e.weight for e in pre_open_graph.entities}
        
        results = manager.open_nodes(["Alice", "Python"])
        assert len(results) == 2, f"Expected 2 entities, got {len(results)}"
        
        # Check weight increments
        graph = manager.read_graph()
        alice = next(e for e in graph.entities if e.name == "Alice")
        python = next(e for e in graph.entities if e.name == "Python")
        assert alice.weight == pre_open_weights["Alice"] + 1, f"Alice weight should be {pre_open_weights['Alice'] + 1}, got {alice.weight}"
        assert python.weight == pre_open_weights["Python"] + 1, f"Python weight should be {pre_open_weights['Python'] + 1}, got {python.weight}"
        print("   PASS open_nodes with weight increment works correctly")
        
        # Test 6: Increment weights manually
        print("6. Testing increment_weights...")
        pre_increment_graph = manager.read_graph()
        pre_increment_weights = {e.name: e.weight for e in pre_increment_graph.entities}
        
        manager.increment_weights(["Alice", "Python"])
        
        graph = manager.read_graph()
        alice = next(e for e in graph.entities if e.name == "Alice")
        python = next(e for e in graph.entities if e.name == "Python")
        assert alice.weight == pre_increment_weights["Alice"] + 1, f"Alice weight should be {pre_increment_weights['Alice'] + 1}, got {alice.weight}"
        assert python.weight == pre_increment_weights["Python"] + 1, f"Python weight should be {pre_increment_weights['Python'] + 1}, got {python.weight}"
        print("   PASS increment_weights works correctly")
        
        # Test 7: Delete observations
        print("7. Testing delete_observations...")
        deletions = [
            {"entityName": "Alice", "observation": "drinks tea sometimes"},
            {"entityName": "Alice", "observation": "nonexistent observation"}  # Should be ignored
        ]
        manager.delete_observations(deletions)
        
        graph = manager.read_graph()
        alice = next(e for e in graph.entities if e.name == "Alice")
        assert "drinks tea sometimes" not in alice.observations
        print("   PASS delete_observations works correctly")
        
        # Test 8: Delete relations
        print("8. Testing delete_relations...")
        manager.delete_relations([
            {"from_entity": "Alice", "to_entity": "Python", "relationType": "uses"}
        ])
        
        graph = manager.read_graph()
        assert len(graph.relations) == 2, f"Expected 2 relations, got {len(graph.relations)}"
        print("   PASS delete_relations works correctly")
        
        # Test 9: Prune entities
        print("9. Testing prune_entities...")
        # Check current weights before pruning
        pre_prune_graph = manager.read_graph()
        print(f"   Pre-prune weights: {[(e.name, e.weight) for e in pre_prune_graph.entities]}")
        
        # Find entities with lowest weights to test pruning
        min_weight = min(e.weight for e in pre_prune_graph.entities)
        threshold = min_weight + 1
        expected_pruned = [e.name for e in pre_prune_graph.entities if e.weight < threshold]
        
        pruned = manager.prune_entities(threshold)
        print(f"   Pruned entities: {pruned}, Expected: {expected_pruned}")
        
        graph = manager.read_graph()
        remaining_names = [e.name for e in graph.entities]
        for name in expected_pruned:
            assert name not in remaining_names, f"{name} should be deleted"
        
        print("   PASS prune_entities with cascade delete works correctly")
        
        # Test 10: Delete entities (cascade)
        print("10. Testing delete_entities...")
        # Create new relation first
        manager.create_relations([Relation("Alice", "Python", "uses")])
        
        manager.delete_entities(["Python"])
        graph = manager.read_graph()
        
        entity_names = [e.name for e in graph.entities]
        assert "Python" not in entity_names, "Python should be deleted"
        assert len(graph.relations) == 0, "Relations to Python should be cascade deleted"
        print("   PASS delete_entities with cascade delete works correctly")
        
        print("\nSUCCESS: All Phase 2 core operations tests passed!")
        print(f"Final graph state: {len(graph.entities)} entities, {len(graph.relations)} relations")
        
        # Show final weights
        print("\nFinal entity weights:")
        for entity in graph.entities:
            print(f"   {entity.name}: weight {entity.weight}")
            
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    test_phase2()
