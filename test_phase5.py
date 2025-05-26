#!/usr/bin/env python3

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from memory_server import KnowledgeGraphManager, Entity, Relation, review_conversation_analysis

def test_phase5():
    """Test Phase 5: Integration Testing - Full workflow and system validation"""
    print("Testing Phase 5: Integration Testing")
    print("=" * 50)
    
    # Use a test file for this phase
    test_file = "test_phase5_memory.jsonl"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    manager = KnowledgeGraphManager(test_file)
    
    # Test 1: Full workflow with sample data
    print("1. Testing full workflow with comprehensive sample data...")
    
    # Create initial dataset representing a project team
    initial_entities = [
        Entity(name="John Smith", entityType="person", observations=["Senior developer", "Python expert"], weight=0),
        Entity(name="Maria Garcia", entityType="person", observations=["Project manager", "Agile coach"], weight=0),
        Entity(name="Alex Chen", entityType="person", observations=["UX designer", "Frontend specialist"], weight=0),
        Entity(name="TechFlow Inc", entityType="organization", observations=["Software consulting company"], weight=0),
        Entity(name="AI Assistant Project", entityType="concept", observations=["Main project for Q4"], weight=0),
        Entity(name="Customer Database", entityType="concept", observations=["MySQL database", "Contains user data"], weight=0),
        Entity(name="San Francisco Office", entityType="location", observations=["Main headquarters", "Downtown location"], weight=0),
    ]
    
    manager.create_entities(initial_entities)
    
    initial_relations = [
        Relation(from_entity="John Smith", to_entity="TechFlow Inc", relationType="works_at"),
        Relation(from_entity="Maria Garcia", to_entity="TechFlow Inc", relationType="works_at"),
        Relation(from_entity="Alex Chen", to_entity="TechFlow Inc", relationType="works_at"),
        Relation(from_entity="John Smith", to_entity="AI Assistant Project", relationType="works_on"),
        Relation(from_entity="Maria Garcia", to_entity="AI Assistant Project", relationType="manages"),
        Relation(from_entity="Alex Chen", to_entity="AI Assistant Project", relationType="designs_for"),
        Relation(from_entity="AI Assistant Project", to_entity="Customer Database", relationType="uses"),
        Relation(from_entity="TechFlow Inc", to_entity="San Francisco Office", relationType="located_at"),
    ]
    
    manager.create_relations(initial_relations)
    
    # Verify initial setup
    graph = manager.read_graph()
    if len(graph.entities) != 7 or len(graph.relations) != 8:
        print(f"   FAIL - Initial setup: Expected 7 entities and 8 relations, got {len(graph.entities)} and {len(graph.relations)}")
        return False
    
    print("   PASS - Initial dataset created successfully")
    
    # Test 2: Verify weight system works correctly across all operations
    print("2. Testing weight system across all operations...")
    
    # Search operations should increment weights
    search_results = manager.search_nodes("John")
    if len(search_results) != 1 or search_results[0].weight != 1:
        print(f"   FAIL - Search weight increment: Expected weight 1, got {search_results[0].weight}")
        return False
    
    # Open operations should increment weights
    open_results = manager.open_nodes(["Maria Garcia", "Alex Chen"])
    if len(open_results) != 2 or open_results[0].weight != 1 or open_results[1].weight != 1:
        print("   FAIL - Open weight increment failed")
        return False
    
    # Manual weight increment
    manager.increment_weights(["TechFlow Inc", "AI Assistant Project"])
    
    # Verify all weight increments
    updated_graph = manager.read_graph()
    entity_weights = {entity.name: entity.weight for entity in updated_graph.entities}
    
    expected_weights = {
        "John Smith": 1,          # search_nodes increment
        "Maria Garcia": 1,        # open_nodes increment  
        "Alex Chen": 1,           # open_nodes increment
        "TechFlow Inc": 1,        # manual increment
        "AI Assistant Project": 1, # manual increment
        "Customer Database": 0,   # no increments
        "San Francisco Office": 0 # no increments
    }
    
    if entity_weights == expected_weights:
        print("   PASS - All weight increments working correctly")
    else:
        print(f"   FAIL - Weight increments: Expected {expected_weights}, got {entity_weights}")
        return False
    
    # Test 3: Test conversation review end-to-end
    print("3. Testing conversation review end-to-end...")
    
    complex_conversation = """
    Maria: Hi everyone, I wanted to discuss our progress on the AI Assistant Project.
    John and Alex have been working hard on the frontend integration.
    
    John: Thanks Maria. I've been focusing on the backend API that connects to our 
    Customer Database. We're using Python with FastAPI framework.
    
    Alex: And I've been designing the user interface. The mockups are ready and 
    I think users will find it intuitive. We should test it with our client DataTech Solutions.
    
    Maria: Great! We also need to coordinate with the Seattle office team. 
    They're handling the deployment infrastructure on AWS.
    
    John: Speaking of deployment, we should consider Docker containers for better 
    scalability. I've been researching container orchestration.
    
    Alex: That sounds good. Also, our meeting with the quality assurance team is 
    scheduled for next Tuesday. They want to review the testing strategy.
    
    Maria: Perfect. Let's make sure we have everything ready for the Q4 roadmap review.
    The board expects to see significant progress on customer engagement metrics.
    """
    
    async def test_conversation_review():
        result = await review_conversation_analysis(complex_conversation, manager=manager)
        
        if not result.get("success", False):
            print(f"   FAIL - Conversation analysis failed: {result.get('error', 'Unknown error')}")
            return False
        
        entities_created = result.get("entities_created", [])
        relations_created = result.get("relations_created", [])
        entities_mentioned = result.get("entities_mentioned", [])
        
        print(f"   Analysis results:")
        print(f"   - Created {len(entities_created)} new entities")
        print(f"   - Created {len(relations_created)} new relations")
        print(f"   - Mentioned {len(entities_mentioned)} entities for weight increments")
        
        # Should extract multiple entities from the rich conversation
        if len(entities_created) < 5:
            print(f"   FAIL - Expected at least 5 entities, got {len(entities_created)}")
            return False
        
        # Should create some relations
        if len(relations_created) < 2:
            print(f"   FAIL - Expected at least 2 relations, got {len(relations_created)}")
            return False
        
        print("   PASS - Conversation analysis extracted appropriate entities and relations")
        return True
    
    # Run async conversation test
    success = asyncio.run(test_conversation_review())
    if not success:
        return False
    
    # Test 4: Validate JSONL storage format
    print("4. Validating JSONL storage format...")
    
    # Force a save and then read the raw file to validate format
    current_graph = manager.read_graph()
    manager.save_graph(current_graph)
    
    # Read raw JSONL file and validate format
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        entity_count = 0
        relation_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"   FAIL - Invalid JSON on line {line_num}: {e}")
                return False
            
            # Validate entity format
            if item.get('type') == 'entity':
                entity_count += 1
                required_fields = ['name', 'entityType', 'observations', 'weight']
                for field in required_fields:
                    if field not in item:
                        print(f"   FAIL - Entity missing required field '{field}': {item}")
                        return False
                
                # Validate field types
                if not isinstance(item['name'], str):
                    print(f"   FAIL - Entity name must be string: {item}")
                    return False
                if not isinstance(item['entityType'], str):
                    print(f"   FAIL - Entity type must be string: {item}")
                    return False
                if not isinstance(item['observations'], list):
                    print(f"   FAIL - Entity observations must be list: {item}")
                    return False
                if not isinstance(item['weight'], int):
                    print(f"   FAIL - Entity weight must be integer: {item}")
                    return False
            
            # Validate relation format
            elif item.get('type') == 'relation':
                relation_count += 1
                required_fields = ['from_entity', 'to_entity', 'relationType']
                for field in required_fields:
                    if field not in item:
                        print(f"   FAIL - Relation missing required field '{field}': {item}")
                        return False
                
                # Validate field types
                if not isinstance(item['from_entity'], str):
                    print(f"   FAIL - Relation from_entity must be string: {item}")
                    return False
                if not isinstance(item['to_entity'], str):
                    print(f"   FAIL - Relation to_entity must be string: {item}")
                    return False
                if not isinstance(item['relationType'], str):
                    print(f"   FAIL - Relation type must be string: {item}")
                    return False
            
            else:
                print(f"   FAIL - Unknown item type: {item}")
                return False
        
        print(f"   PASS - JSONL format validated: {entity_count} entities, {relation_count} relations")
        
    except Exception as e:
        print(f"   FAIL - JSONL validation error: {e}")
        return False
    
    # Test 5: Test pruning functionality in integrated environment
    print("5. Testing pruning in integrated environment...")
    
    # Add some low-weight entities
    low_weight_entities = [
        Entity(name="Temporary Task", entityType="concept", observations=["Short-term task"], weight=0),
        Entity(name="Old Meeting", entityType="concept", observations=["Past meeting"], weight=1),
        Entity(name="Deprecated Tool", entityType="concept", observations=["No longer used"], weight=0),
    ]
    
    manager.create_entities(low_weight_entities)
    
    # Create relations involving these entities
    temp_relations = [
        Relation(from_entity="John Smith", to_entity="Temporary Task", relationType="worked_on"),
        Relation(from_entity="Maria Garcia", to_entity="Old Meeting", relationType="attended"),
    ]
    
    manager.create_relations(temp_relations)
    
    # Count before pruning
    pre_prune_graph = manager.read_graph()
    pre_prune_entity_count = len(pre_prune_graph.entities)
    pre_prune_relation_count = len(pre_prune_graph.relations)
    
    # Debug: Check current weights before pruning
    print("   Current entity weights before pruning:")
    for entity in pre_prune_graph.entities:
        print(f"     {entity.name}: weight={entity.weight}")
    
    # Use a higher threshold since conversation analysis incremented weights
    # Most entities now have weight >= 1, so use threshold 3 to prune only very low weight ones
    pruned_names = manager.prune_entities(threshold=3)
    
    # Count after pruning
    post_prune_graph = manager.read_graph()
    post_prune_entity_count = len(post_prune_graph.entities)
    post_prune_relation_count = len(post_prune_graph.relations)
    
    # Should have pruned entities with weight < 3
    # Expected pruned should be entities with weights 0, 1, 2
    # Let's check what was actually pruned
    print(f"   Pruned {len(pruned_names)} entities: {pruned_names}")
    
    # Verify some entities were pruned
    if len(pruned_names) > 0:
        print("   PASS - Entities pruned from integrated environment")
    else:
        print("   FAIL - No entities were pruned")
        return False
    
    # Relations should also be pruned
    if post_prune_relation_count < pre_prune_relation_count:
        print("   PASS - Relations properly cascade deleted during pruning")
    else:
        print("   FAIL - Relations not properly cascade deleted")
        return False
    
    # Test 6: Test data persistence across operations
    print("6. Testing data persistence across multiple operations...")
    
    # Perform multiple operations and verify data consistency
    operations = [
        ("search", lambda: manager.search_nodes("TechFlow")),
        ("open", lambda: manager.open_nodes(["John Smith", "AI Assistant Project"])),
        ("add_obs", lambda: manager.add_observations([
            {"entityName": "John Smith", "observation": "Leads backend development"},
            {"entityName": "Maria Garcia", "observation": "Scrum master certified"}
        ])),
        ("create_entity", lambda: manager.create_entities([
            Entity(name="Integration Test", entityType="concept", observations=["Test entity"], weight=10)  # High weight to survive pruning
        ])),
        ("create_relation", lambda: manager.create_relations([
            Relation(from_entity="Integration Test", to_entity="Integration Test", relationType="self_reference")  # Self-reference to avoid dangling
        ])),
    ]
    
    # Execute all operations
    for op_name, op_func in operations:
        try:
            op_func()
        except Exception as e:
            print(f"   FAIL - Operation {op_name} failed: {e}")
            return False
    
    # Verify final state
    final_graph = manager.read_graph()
    
    # Check if Integration Test entity was created
    integration_entity = None
    for entity in final_graph.entities:
        if entity.name == "Integration Test":
            integration_entity = entity
            break
    
    if integration_entity is None:
        print("   FAIL - Integration Test entity not found after creation")
        return False
    
    if integration_entity.weight != 10:
        print(f"   FAIL - Integration Test entity weight incorrect: expected 10, got {integration_entity.weight}")
        return False
    
    # Check if Integration Test relation was created
    integration_relation = None
    for relation in final_graph.relations:
        if relation.from_entity == "Integration Test" and relation.to_entity == "Integration Test":
            integration_relation = relation
            break
    
    if integration_relation is None:
        print("   FAIL - Integration Test relation not found after creation")
        return False
    
    print("   PASS - All operations persisted correctly")
    
    # Test 7: Performance and load testing
    print("7. Testing performance with larger dataset...")
    
    # Create a larger dataset
    large_entities = []
    for i in range(50):
        entity = Entity(
            name=f"Entity_{i:02d}",
            entityType="test",
            observations=[f"Test observation {i}", f"Additional info {i}"],
            weight=i % 10  # Varied weights
        )
        large_entities.append(entity)
    
    # Time the operation (basic performance check)
    import time
    start_time = time.time()
    manager.create_entities(large_entities)
    end_time = time.time()
    
    creation_time = end_time - start_time
    if creation_time > 5.0:  # Should complete within 5 seconds
        print(f"   FAIL - Large entity creation too slow: {creation_time:.2f}s")
        return False
    
    # Test large search operation
    start_time = time.time()
    search_results = manager.search_nodes("Entity")
    end_time = time.time()
    
    search_time = end_time - start_time
    if search_time > 2.0:  # Should complete within 2 seconds
        print(f"   FAIL - Large search operation too slow: {search_time:.2f}s")
        return False
    
    if len(search_results) < 40:  # Should find most entities
        print(f"   FAIL - Search found too few entities: {len(search_results)}")
        return False
    
    print(f"   PASS - Performance acceptable (create: {creation_time:.2f}s, search: {search_time:.2f}s)")
    
    # Final verification: Check final graph state
    print("8. Final system state verification...")
    
    final_graph = manager.read_graph()
    print(f"   Final graph contains {len(final_graph.entities)} entities and {len(final_graph.relations)} relations")
    
    # Check for data integrity
    entity_names = {entity.name for entity in final_graph.entities}
    relation_entity_names = set()
    for relation in final_graph.relations:
        relation_entity_names.add(relation.from_entity)
        relation_entity_names.add(relation.to_entity)
    
    # All entities referenced in relations should exist
    missing_entities = relation_entity_names - entity_names
    if missing_entities:
        print(f"   FAIL - Relations reference non-existent entities: {missing_entities}")
        return False
    
    print("   PASS - Final data integrity verified")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\nSUCCESS: All Phase 5 integration tests passed!")
    print("Full system workflow validated successfully.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_phase5()
        if success:
            print("\n" + "=" * 60)
            print("PHASE 5 INTEGRATION TESTING COMPLETED SUCCESSFULLY!")
            print("All systems are working correctly:")
            print("* Full workflow with comprehensive sample data")
            print("* Weight system accuracy across all operations")
            print("* Conversation review end-to-end functionality")
            print("* JSONL storage format validation")
            print("* Data persistence and integrity")
            print("* Performance with larger datasets")
            print("* System integration and error handling")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\nFAILED: Phase 5 integration testing failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Phase 5 testing crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
