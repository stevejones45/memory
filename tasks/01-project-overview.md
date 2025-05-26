# Python Memory Server - Project Overview

## Goal
Refactor the TypeScript MCP memory server to Python with enhanced weight tracking and conversation review capabilities.

## Key Requirements
- Keep implementation simple and minimal
- Direct port of existing functionality
- Add weight system for entity usage tracking
- Add conversation review tool for automatic memory extraction
- Maintain same MCP interface
- Use JSONL storage format
- No compatibility with existing memory files needed

## Core Enhancements
1. **Weight System**: Track entity usage frequency for conceptual framework mapping
2. **Conversation Review**: Automatic extraction and storage of conversation insights
3. **Graph Pruning**: Remove low-weight entities below threshold

## Target Architecture
- Single Python file implementation
- Python MCP SDK
- JSONL storage with weight field
- 11 total MCP tools (9 existing + 2 new)
