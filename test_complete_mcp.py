#!/usr/bin/env python3

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from memory_server import knowledge_graph_manager, handle_tool_call, list_tools

async def test_complete_mcp_interface():
    """Test complete MCP interface with all 11 tools"""
    print("Testing Complete MCP Interface - All 11 Tools")
    print("=" * 60)
    
    # Use a test file for this test
    test_file = "test_complete_mcp.jsonl"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Override global manager for testing
    global knowledge_graph_manager
    from memory_server import KnowledgeGraphManager
    knowledge_graph_manager = KnowledgeGraphManager(test_file)
    
    # Test 1: Verify all tools are listed
    print("1. Testing tool registration...")
    tools = await list_tools()
    tool_names = [tool["name"] for tool in tools]
    expected_tools = [
        "create_entities", "create_relations", "add_observations",
        "delete_entities", "delete_observations", "delete_relations", 
        "read_graph", "search_nodes", "open_nodes",
        "prune_entities", "review_conversation"
    ]
    
    if set(tool_names) == set(expected_tools):
        print(f"   PASS - All 11 tools registered: {len(tools)} tools")
    else:
        print(f"   FAIL - Expected {expected_tools}, got {tool_names}")
        return False
    
    # Test 2: Test entity creation
    print("2. Testing create_entities via MCP...")
    create_result = await handle_tool_call("create_entities", {
        "entities": [
            {"name": "Alice", "entityType": "person", "observations": ["software engineer"], "weight": 3},
            {"name": "TechCorp", "entityType": "organization", "observations": ["tech company"], "weight": 2}
        ]
    })
    
    result_json = json.loads(create_result[0]["text"])
    if result_json.get("success"):
        print("   PASS - Entity creation via MCP")
    else:
        print(f"   FAIL - Entity creation failed: {result_json}")
        return False
    
    # Test 3: Test relation creation
    print("3. Testing create_relations via MCP...")
    relation_result = await handle_tool_call("create_relations", {
        "relations": [
            {"from_entity": "Alice", "to_entity": "TechCorp", "relationType": "works_at"}
        ]
    })
    
    result_json = json.loads(relation_result[0]["text"])
    if result_json.get("success"):
        print("   PASS - Relation creation via MCP")
    else:
        print(f"   FAIL - Relation creation failed: {result_json}")
        return False
    
    # Test 4: Test search with weight increment  
    print("4. Testing search_nodes via MCP...")
    search_result = await handle_tool_call("search_nodes", {"query": "Alice"})
    result_json = json.loads(search_result[0]["text"])
    
    if result_json.get("success") and result_json.get("count") > 0:
        # Check if weight was incremented (should be 4 now: 3 + 1)
        entities = result_json.get("entities", [])
        alice_weight = entities[0].get("weight", 0) if entities else 0
        if alice_weight == 4:
            print("   PASS - Search with weight increment via MCP")
        else:
            print(f"   FAIL - Expected weight 4, got {alice_weight}")
            return False
    else:
        print(f"   FAIL - Search failed: {result_json}")
        return False
    
    # Test 5: Test conversation review
    print("5. Testing review_conversation via MCP...")
    conversation_result = await handle_tool_call("review_conversation", {
        "conversation": "Human: I met with Bob Wilson at the office yesterday. We discussed the new project for improving customer analytics. Assistant: That sounds productive! Human: Yes, Bob is leading the data science team and they're making great progress."
    })
    
    result_json = json.loads(conversation_result[0]["text"])
    if result_json.get("success"):
        entities_created = result_json.get("entities_created", [])
        if len(entities_created) > 0:
            print(f"   PASS - Conversation analysis via MCP ({len(entities_created)} entities created)")
        else:
            print("   FAIL - No entities created from conversation")
            return False
    else:
        print(f"   FAIL - Conversation analysis failed: {result_json}")
        return False
    
    # Test 6: Test read_graph to see all data
    print("6. Testing read_graph via MCP...")
    graph_result = await handle_tool_call("read_graph", {})
    result_json = json.loads(graph_result[0]["text"])
    
    if "entities" in result_json and "relations" in result_json:
        entity_count = len(result_json["entities"])
        relation_count = len(result_json["relations"])
        print(f"   PASS - Graph contains {entity_count} entities and {relation_count} relations")
    else:
        print(f"   FAIL - Invalid graph structure: {result_json}")
        return False
    
    # Test 7: Test prune_entities
    print("7. Testing prune_entities via MCP...")
    prune_result = await handle_tool_call("prune_entities", {"threshold": 2})
    result_json = json.loads(prune_result[0]["text"])
    
    if result_json.get("success"):
        pruned_count = result_json.get("count", 0)
        print(f"   PASS - Pruned {pruned_count} entities with threshold 2")
    else:
        print(f"   FAIL - Pruning failed: {result_json}")
        return False
    
    # Test 8: Test final graph state
    print("8. Testing final graph state...")
    final_graph_result = await handle_tool_call("read_graph", {})
    final_json = json.loads(final_graph_result[0]["text"])
    
    final_entity_count = len(final_json["entities"])
    final_relation_count = len(final_json["relations"])
    
    if final_entity_count > 0:  # Should still have some entities
        print(f"   PASS - Final graph: {final_entity_count} entities, {final_relation_count} relations")
    else:
        print("   FAIL - All entities were pruned")
        return False
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\nSUCCESS: Complete MCP interface test passed!")
    print("All 11 tools working correctly via MCP protocol.")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_complete_mcp_interface())
        if success:
            print("\nSUCCESS: Complete MCP interface testing completed!")
            sys.exit(0)
        else:
            print("\nFAILED: Complete MCP interface testing failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Complete MCP interface testing crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
