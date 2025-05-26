#!/usr/bin/env python3

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from memory_server import KnowledgeGraphManager, Entity, Relation, review_conversation_analysis

def test_phase4():
    """Test Phase 4: New Functionality (prune_entities and review_conversation)"""
    print("Testing Phase 4: New Functionality")
    print("=" * 50)
    
    # Use a test file for this phase
    test_file = "test_phase4_memory.jsonl"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    manager = KnowledgeGraphManager(test_file)
    
    # Test 1: Set up test data with various weights
    print("1. Setting up test data with various weights...")
    test_entities = [
        Entity(name="Alice", entityType="person", observations=["works at tech corp"], weight=5),
        Entity(name="Bob", entityType="person", observations=["manager"], weight=3), 
        Entity(name="Charlie", entityType="person", observations=["intern"], weight=1),
        Entity(name="Diana", entityType="person", observations=["CEO"], weight=0),
        Entity(name="TechCorp", entityType="organization", observations=["software company"], weight=4),
        Entity(name="Project Alpha", entityType="concept", observations=["main project"], weight=2),
        Entity(name="Old Task", entityType="concept", observations=["deprecated"], weight=0),
    ]
    
    manager.create_entities(test_entities)
    
    # Create some relations
    test_relations = [
        Relation(from_entity="Alice", to_entity="TechCorp", relationType="works_at"),
        Relation(from_entity="Bob", to_entity="TechCorp", relationType="works_at"),
        Relation(from_entity="Charlie", to_entity="TechCorp", relationType="works_at"),
        Relation(from_entity="Diana", to_entity="TechCorp", relationType="leads"),
        Relation(from_entity="Alice", to_entity="Project Alpha", relationType="works_on"),
        Relation(from_entity="Bob", to_entity="Old Task", relationType="worked_on"),
    ]
    
    manager.create_relations(test_relations)
    
    # Verify initial state
    graph = manager.read_graph()
    print(f"   Created {len(graph.entities)} entities and {len(graph.relations)} relations")
    
    # Test 2: Test prune_entities functionality
    print("2. Testing prune_entities functionality...")
    
    # Test pruning with threshold 2 (should remove Charlie, Diana, Old Task)
    pruned_names = manager.prune_entities(threshold=2)
    expected_pruned = {"Charlie", "Diana", "Old Task"}
    
    if set(pruned_names) == expected_pruned:
        print("   PASS - Correct entities pruned")
    else:
        print(f"   FAIL - Expected {expected_pruned}, got {set(pruned_names)}")
        return False
    
    # Verify entities were actually removed
    graph_after_prune = manager.read_graph()
    remaining_names = {entity.name for entity in graph_after_prune.entities}
    expected_remaining = {"Alice", "Bob", "TechCorp", "Project Alpha"}
    
    if remaining_names == expected_remaining:
        print("   PASS - Entities properly removed from graph")
    else:
        print(f"   FAIL - Expected {expected_remaining}, got {remaining_names}")
        return False
    
    # Verify cascade deletion of relations
    remaining_relations = graph_after_prune.relations
    relation_tuples = {(r.from_entity, r.to_entity, r.relationType) for r in remaining_relations}
    
    # Should have removed relations involving Charlie, Diana, and Old Task
    expected_relations = {
        ("Alice", "TechCorp", "works_at"),
        ("Bob", "TechCorp", "works_at"), 
        ("Alice", "Project Alpha", "works_on")
    }
    
    if relation_tuples == expected_relations:
        print("   PASS - Relations properly cascade deleted")
    else:
        print(f"   FAIL - Expected {expected_relations}, got {relation_tuples}")
        return False
    
    # Test 3: Test conversation review functionality
    print("3. Testing review_conversation functionality...")
    
    sample_conversation = """
    Human: Hi, I'm working on a new project with Sarah Johnson at our downtown office.
    We're developing a machine learning algorithm for customer analytics.
    
    Assistant: That sounds interesting! How is the project progressing?
    
    Human: Pretty well. Sarah is the team lead and she's been coordinating with 
    the marketing department. We have a meeting scheduled for next week to discuss
    the database integration with our main server.
    
    Assistant: Good luck with your meeting! Is this part of the Q4 roadmap?
    
    Human: Yes, it's one of our key goals this quarter. The company wants to improve
    customer retention by 15% using data-driven insights.
    """
    
    # Test conversation analysis
    async def test_conversation_analysis():
        result = await review_conversation_analysis(sample_conversation, manager=manager)
        
        if not result.get("success", False):
            print(f"   FAIL - Conversation analysis failed: {result.get('error', 'Unknown error')}")
            return False
        
        entities_created = result.get("entities_created", [])
        relations_created = result.get("relations_created", [])
        
        print(f"   Created {len(entities_created)} entities: {entities_created}")
        print(f"   Created {len(relations_created)} relations")
        
        # Check if at least some entities were extracted
        if len(entities_created) > 0:
            print("   PASS - Entities extracted from conversation")
        else:
            print("   FAIL - No entities extracted from conversation")
            return False
        
        return True
    
    # Run async test
    success = asyncio.run(test_conversation_analysis())
    if not success:
        return False
    
    # Test 4: Verify conversation entities were added to graph
    print("4. Verifying conversation entities added to graph...")
    final_graph = manager.read_graph()
    final_entity_names = {entity.name for entity in final_graph.entities}
    
    # Should have original entities plus new ones from conversation
    original_count = len(expected_remaining)  # 4 entities after pruning
    final_count = len(final_graph.entities)
    
    if final_count > original_count:
        print(f"   PASS - New entities added from conversation ({final_count - original_count} new entities)")
    else:
        print(f"   FAIL - No new entities added from conversation (had {original_count}, now have {final_count})")
        print(f"   Final entity names: {final_entity_names}")
        return False
    
    # Test 5: Test empty prune (threshold 0)
    print("5. Testing prune with threshold 0...")
    pruned_zero = manager.prune_entities(threshold=0)
    
    if len(pruned_zero) == 0:
        print("   PASS - No entities pruned with threshold 0")
    else:
        print(f"   FAIL - Unexpected entities pruned: {pruned_zero}")
        return False
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\nSUCCESS: All Phase 4 functionality tests passed!")
    print("New tools (prune_entities and review_conversation) are working correctly.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_phase4()
        if success:
            print("\nSUCCESS: Phase 4 testing completed successfully!")
            sys.exit(0)
        else:
            print("\nFAILED: Phase 4 testing failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Phase 4 testing crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
