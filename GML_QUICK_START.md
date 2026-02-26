# GML Quick Start

## What is GML?

GML (Gigzs Memory Layer) gives your chatbot **true long-term memory**. It remembers people, places, relationships, and events across conversations.

## 5-Minute Setup

### 1. It's Already Integrated!

Both the web app and CLI chatbot automatically use GML. Just start them:

```powershell
# Web app
python app.py

# Or CLI voice assistant
python main.py
```

### 2. Use Memory Commands in CLI

**Tell bot to remember:**
```
User: "Remember that I like Python programming"
Bot: "Got it! I'll remember that: I like Python programming"
```

**Ask bot to recall:**
```
User: "What do you remember about me?"
Bot: "I remember: User told me they like Python programming"
```

**Check memory status:**
```
User: "Memory status"
Bot: "My memory currently has 5 entities, 3 relationships, and 12 events."
```

### 3. Use Memory API in Web App

Check `GML_GUIDE.md` for full API reference. Key endpoints:

```bash
# Search memory
curl -X POST http://localhost:5000/api/memory/recall \
  -H "Content-Type: application/json" \
  -d '{"query":"What do you remember?"}'

# Add entity
curl -X POST http://localhost:5000/api/memory/entity \
  -H "Content-Type: application/json" \
  -d '{"name":"John","type":"person"}'

# Get memory stats
curl http://localhost:5000/api/memory/stats
```

## Key Features

| Feature | What It Does |
|---------|-------------|
| **Entities** | Remembers people, places, concepts |
| **Relationships** | Understands "Alice knows Bob" |
| **Events** | Logs conversations with timestamps |
| **Semantic Search** | Finds memories by meaning |
| **Memory Decay** | Old memories naturally fade |
| **Persistence** | Saves to `gml_memory.json` |

## Usage Examples

### Example 1: User Profile 

```
Day 1:
User: "I'm a Python developer from New York"
Bot: Creates "You" entity with attributes, location

Day 2:
User: "What do you know about me?"
Bot: "You're a Python developer from New York"
```

### Example 2: Relationships

```
Day 1:
User: "I work with Alice on AI projects"
Bot: Creates entities, links with "works_with" relationship

Later:
User: "Who do I collaborate with?"
Bot: "You work with Alice on AI projects"
```

### Example 3: Auto-Logging

Every conversation is automatically logged:
- User messages → stored as events
- Bot responses → associated with events
- Entities mentioned → automatically extracted
- Relationships inferred → connections created

No extra work needed!

## Memory File

Memories stored in: **`gml_memory.json`**

```json
{
  "entities": {
    "person_123": {
      "name": "Alice",
      "type": "person",
      "attributes": {"profession": "engineer"}
    }
  },
  "relationships": [
    {
      "from": "person_123",
      "to": "person_456",
      "type": "knows",
      "strength": 0.85
    }
  ],
  "events": [...]
}
```

## Python Usage

Quick code example:

```python
from gml import GigzsMemoryLayer

gml = GigzsMemoryLayer()

# Add entities
alice = gml.add_entity("Alice", "person", {"age": 25})
bob = gml.add_entity("Bob", "person", {"age": 30})

# Create relationship
gml.add_relationship(alice, bob, "knows")

# Log event
gml.log_event("Alice and Bob started a project", [alice, bob])

# Recall
result = gml.recall("What do I know?")

# Save
gml.save_memory()
```

## Common Commands

### CLI Voice Assistant

| Say This | What Happens |
|----------|-------------|
| "Remember that..." | Stores memory |
| "Recall..." | Searches memory |
| "What do you remember?" | Shows related memories |
| "Memory status" | Shows stats |

### Web API

| Endpoint | Purpose |
|----------|---------|
| `POST /api/memory/recall` | Search memories |
| `POST /api/memory/entity` | Add person/place/concept |
| `POST /api/memory/relationship` | Link two entities |
| `POST /api/memory/event` | Log interaction |
| `GET /api/memory/stats` | See memory size |

## Tips & Tricks

**💡 Tip 1**: Memories strengthen when mentioned multiple times
```
User: "Remember Alice"
User: "Alice is my friend"
→ Alice's importance score increases
```

**💡 Tip 2**: Use natural language - GML understands context
```
"The engineer I met" → links to Alice (engineer entity)
"My colleague" → links to recent work relationships
```

**💡 Tip 3**: Check memory before processing
```
# Queries like "who did I meet?" automatically search memory
→ Returns all "meets" events with confidence scores
```

**💡 Tip 4**: Export memory as needed
```python
with open('my_memory.json', 'r') as f:
    data = json.load(f)
# Backup or analyze
```

## Common Issues

**Q: Memory not appearing?**
- A: Memories auto-save every 5 interactions. Force save:
  ```bash
  curl -X POST http://localhost:5000/api/memory/save
  ```

**Q: Memory file too large?**
- A: Clean up old memories:
  ```python
  gml.apply_memory_decay(days=30)
  gml.save_memory()
  ```

**Q: Want to reset?**
- A: Clear all memories:
  ```bash
  curl -X POST http://localhost:5000/api/memory/clear
  ```

**Q: How do I check what's stored?**
- A: Open `gml_memory.json` in your editor, or use:
  ```bash
  curl http://localhost:5000/api/memory/stats
  ```

## Next Steps

1. **Start bot**: `python app.py` or `python main.py`
2. **Create memories**: Use natural language commands
3. **Recall**: Ask "what do you remember?"
4. **Check stats**: See how much memory is used
5. **Read full docs**: See `GML_GUIDE.md` for advanced features

## Architecture Overview

```
┌─────────────────────────────────────┐
│   Your Chatbot (Flask + CLI)        │
└────────┬────────────────────────────┘
         │
         │ Every conversation
         │ passes through
         │
┌────────▼────────────────────────────┐
│   Gigzs Memory Layer (GML)          │
│  ├─ Entity Store (people, places)   │
│  ├─ Relationships (knows, likes)    │
│  ├─ Events (conversations)          │
│  ├─ Vector Search (semantic)        │
│  └─ Memory Decay (forgetting)       │
└────────┬────────────────────────────┘
         │
         │ Persistence
         │
┌────────▼────────────────────────────┐
│   gml_memory.json (Local Storage)   │
└─────────────────────────────────────┘
```

## Resources

- **Full Guide**: `GML_GUIDE.md` - Complete reference
- **Code**: `gml.py` - 700+ lines of memory logic
- **API Docs**: See Flask endpoints in `app.py`
- **CLI Integration**: See `main.py` for voice commands

## The Big Idea

Instead of this:

```
User: "I met Alice yesterday"
User: "What was her name?"
Bot: "I don't know" ❌
```

Now you get this:

```
User: "I met Alice yesterday" 
Bot: Creates entity "Alice", logs meeting event

User: "Who did I meet yesterday?"
Bot: "You met Alice" ✓
```

**That's the power of GML.** 🧠✨

---

**Questions?** Check `GML_GUIDE.md` for the full documentation.

