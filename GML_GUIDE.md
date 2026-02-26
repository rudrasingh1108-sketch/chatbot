# Gigzs Memory Layer (GML) - Complete Guide

## What is GML?

**Gigzs Memory Layer (GML)** is a semantic, relational memory system that gives your AI chatbot **true long-term recall**. Unlike traditional systems that forget after each conversation, GML maintains intelligent memories across time through:

- **Entity Recognition**: Remembers people, places, and concepts
- **Relationship Tracking**: Understands how entities connect to each other
- **Event Logging**: Records time-bound interactions with confidence scoring
- **Semantic Search**: Recalls memories through meaning, not keywords
- **Memory Decay**: Intelligently forgets less important memories over time
- **Temporal Awareness**: Understands when things happened and their relevance

## The Problem GML Solves

**Traditional AI**: "Tell me about your friend"
- User: "I met a girl yesterday"
- User (next day): "The girl I met yesterday, did I like her?"
- **Bot**: "I don't know who that is" ❌

**With GML**: 
- Bot: "Yes, you said you really liked her and you want to see her again" ✓

GML links entities across time and reasons about relationships, not raw text.

## Architecture

### Core Components

```
GigzsMemoryLayer
├── Entities (people, places, concepts)
├── Relationships (knows, likes, works_with, etc.)
├── Events (interactions, conversations, achievements)
├── VectorEmbedding (semantic search via TF-IDF)
└── Memory Management (decay, consolidation, persistence)
```

### How It Works

1. **Encoding**: Conversations are parsed into entities, relationships, and events
2. **Embedding**: Text converted to vector representations using TF-IDF
3. **Storage**: Data persisted as JSON with metadata (confidence, timestamps)
4. **Recall**: Semantic similarity search finds relevant memories
5. **Decay**: Older, less important memories naturally fade
6. **Consolidation**: Related memories are summarized and linked

## Using GML in Your Chatbot

### Web Application (Flask)

GML is automatically integrated! Every conversation is logged to memory.

#### API Endpoints

**1. Recall Memories**
```
POST /api/memory/recall

{
  "query": "What do you remember about John?",
  "recall_type": "all"  // "all", "entities", "events"
}

Response:
{
  "query": "What do you remember about John?",
  "entities": [
    {
      "id": "person_abc123",
      "name": "John",
      "type": "person",
      "similarity": 0.95,
      "attributes": {"age": 30, "profession": "engineer"}
    }
  ],
  "events": [...],
  "relationships": [...]
}
```

**2. Manually Add Entity**
```
POST /api/memory/entity

{
  "name": "Alice Johnson",
  "type": "person",
  "attributes": {
    "age": 25,
    "profession": "designer",
    "city": "New York"
  }
}

Response:
{
  "status": "Entity added",
  "entity_id": "person_xyz789",
  "name": "Alice Johnson",
  "type": "person"
}
```

**3. Search Entities**
```
GET /api/memory/entity/engineer

Response:
{
  "query": "engineer",
  "entities": [
    {
      "id": "person_abc123",
      "name": "John",
      "type": "person",
      "similarity": 0.87,
      "attributes": {...}
    }
  ]
}
```

**4. Get Full Entity Information**
```
GET /api/memory/entity-info/Alice

Response:
{
  "entity": {
    "id": "person_def456",
    "name": "Alice",
    "type": "person",
    "attributes": {...},
    "last_mentioned": "2026-02-26T15:30:00.000000"
  },
  "events": [
    {
      "description": "User: 'Alice is my colleague' | Bot: 'Got it!'",
      "type": "conversation",
      "timestamp": "2026-02-26T15:30:00.000000",
      "confidence": 0.8
    }
  ],
  "relationships": [
    {
      "source_id": "person_abc123",
      "target_id": "person_def456",
      "type": "knows",
      "strength": 0.8
    }
  ]
}
```

**5. Add Relationship**
```
POST /api/memory/relationship

{
  "source_entity": "John",
  "target_entity": "Alice",
  "relationship_type": "works_with",
  "context": "They collaborate on ML projects"
}

Response:
{
  "status": "Relationship added",
  "source": "John",
  "target": "Alice",
  "type": "works_with"
}
```

**6. Log Event (Interaction)**
```
POST /api/memory/event

{
  "description": "User told me they want to learn Python",
  "entity_names": ["John"],
  "event_type": "goal"
}

Response:
{
  "status": "Event logged",
  "event_id": "event_123",
  "description": "User told me...",
  "entities": ["John"]
}
```

**7. Memory Statistics**
```
GET /api/memory/stats

Response:
{
  "statistics": {
    "total_entities": 12,
    "total_relationships": 8,
    "total_events": 45,
    "vocabulary_size": 234
  },
  "consolidation": {
    "total_entities": 12,
    "total_relationships": 8,
    "total_events": 45,
    "entities_by_type": {
      "person": [["John", 0.95], ["Alice", 0.87]],
      "place": [["New York", 0.72]]
    }
  }
}
```

**8. Save Memory (Manual)**
```
POST /api/memory/save

Response:
{
  "status": "Memory saved successfully"
}
```

**9. Clear All Memories**
```
POST /api/memory/clear

Response:
{
  "status": "All memories cleared"
}
```

### CLI Application (Voice Assistant)

GML is integrated into the voice chatbot with natural commands:

#### Memory Commands

**Remember Something**
```
User: "Remember that I like hiking"
Bot: "Got it! I'll remember that: I like hiking"

User: "Add to memory that I work as an engineer"
Bot: "Got it! I'll add that to my memory"
```

**Recall Memories**
```
User: "What do you remember about me?"
Bot: "I remember: User told me they like hiking and work as an engineer"

User: "Remind me what hobbies I mentioned"
Bot: "You told me you like hiking"

User: "Recall our conversations"
Bot: "I remember several interactions we've had..."
```

**Check Memory Status**
```
User: "Memory status"
Bot: "My memory currently has 5 entities, 3 relationships, and 12 events."

User: "How much do you remember?"
Bot: "My memory currently has 5 entities, 3 relationships, and 12 events."
```

## Memory Persistence

**File**: `gml_memory.json`

GML automatically saves conversations to disk. You can also manually trigger saves:

```python
gml.save_memory()  # Programmatically
```

**Web API**:
```bash
curl -X POST http://localhost:5000/api/memory/save
```

The file structure:
```json
{
  "timestamp": "2026-02-26T15:30:00.000000",
  "entities": {
    "person_abc123": {
      "id": "person_abc123",
      "name": "John",
      "type": "person",
      "attributes": {...},
      "importance_score": 0.95,
      "last_mentioned": "2026-02-26T15:30:00.000000"
    }
  },
  "relationships": [
    {
      "source_id": "person_abc123",
      "target_id": "person_def456",
      "type": "knows",
      "strength": 0.8
    }
  ],
  "events": [...]
}
```

## Python API

### Basic Usage

```python
from gml import GigzsMemoryLayer

# Initialize
gml = GigzsMemoryLayer()

# Add entities
alice_id = gml.add_entity("Alice", "person", {"age": 25})
bob_id = gml.add_entity("Bob", "person", {"age": 30})

# Create relationships
gml.add_relationship(alice_id, bob_id, "knows", "met at conference")

# Log events
event_id = gml.log_event(
    "Alice and Bob collaborated on ML project",
    [alice_id, bob_id],
    "collaboration"
)

# Recall memories
result = gml.recall("Who do I know?")
print(result)

# Get specific entity info
info = gml.recall_about_entity("Alice")
print(info)

# Save to disk
gml.save_memory()
```

### Advanced Usage

**Search by Semantic Similarity**
```python
# Find entities matching a query
results = gml.search_entities("machine learning expert")
for entity_id, similarity_score in results:
    entity = gml.get_entity(entity_id)
    print(f"{entity.name} (similarity: {similarity_score:.2f})")
```

**Get Relationships**
```python
# Get all relationships for entity
relationships = gml.get_relationships(alice_id, direction="outgoing")
for rel in relationships:
    print(f"{rel.source_id} --{rel.type}--> {rel.target_id}")
```

**Memory Decay**
```python
# Apply temporal decay (call periodically)
gml.apply_memory_decay(days=1)

# Consolidate memories
summary = gml.consolidate_memories()
print(summary)
```

**Entity Updates**
```python
# Get entity and update
entity = gml.get_entity(entity_id)
gml.update_entity_attribute(entity_id, "profession", "architect")
```

## Confidence & Importance Scoring

Every memory has confidence and importance scores:

- **Confidence**: 0-1 (how reliable is this memory?)
- **Importance**: 0-1 (how relevant is this memory?)

These affect:
- Memory decay (less important memories fade faster)
- Recall ranking (more important memories returned first)
- Consolidation (low-importance memories may be summarized)

```python
event = gml.events[event_id]
print(f"Confidence: {event.confidence}")  # 0.95
print(f"Importance: {event.importance}")  # 0.8
```

## Memory Decay & Forgetting

GML implements intelligent memory decay:

- **Daily decay**: Memories lose 1% importance per day by default
- **Event threshold**: Events older than 365 days are forgotten
- **Low-importance threshold**: Memories below 0.1 importance are removed
- **Relationship decay**: Unused relationships gradually weaken

```python
# Decay memories daily
gml.apply_memory_decay(days=1)

# Values
gml.memory_decay_factor = 0.99      # 99% retained daily
gml.memory_decay_threshold = 0.1    # Below this = forgotten
```

## Entity Types

GML supports multiple entity types:

| Type | Examples | Common Attributes |
|------|----------|-------------------|
| `person` | Alice, Mom, Teacher | age, profession, city, relationship |
| `place` | New York, Office, School | location, country, visited |
| `concept` | Python, ML, Music | description, related_concepts |
| `organization` | Microsoft, School | type, size, location |
| `event` | Birthday, Meeting | date, location, attendees |

```python
gml.add_entity("Python", "concept", {"category": "programming_language"})
gml.add_entity("Microsoft", "organization", {"type": "tech_company", "hq": "Seattle"})
```

## Relationship Types

Common relationship types:

| Type | Meaning | Example |
|------|---------|---------|
| `knows` | Two people know each other | Alice knows Bob |
| `likes` | One entity likes another | John likes hiking |
| `works_with` | Collaboration | Alice works with Bob |
| `located_in` | Location relationship | Alice lives in New York |
| `parent_of` | Family relationship | Mom is parent of Alice |
| `part_of` | Composition | Python is part of ML stack |
| `causes` | Causal relationship | Exercise causes fitness |

```python
gml.add_relationship(alice_id, python_id, "interested_in")
gml.add_relationship(alice_id, ny_id, "lives_in")
```

## Event Types

Event categories:

- `conversation`: Regular chat
- `interaction`: User-bot exchange
- `important_note`: User explicitly wants remembered
- `collaboration`: Multiple entities working together
- `goal`: User's stated objectives
- `achievement`: Accomplishment
- `question`: User asking something

## Memory Consolidation

Periodically consolidate memories to reduce redundancy:

```python
consolidation = gml.consolidate_memories()
# Returns summary of memory structure

print(f"Total entities: {consolidation['total_entities']}")
print(f"Total relationships: {consolidation['total_relationships']}")
print(f"Total events: {consolidation['total_events']}")
```

## Integration with Emotion Analyzer

GML integrates with your emotion detection:

```python
# In app.py, emotions are automatically stored
if emotion_detected == "stress":
    gml.update_entity_attribute(user_id, "last_emotion", "stress")
```

## Privacy & Security

**Key Points**:
- All memory stored locally (no cloud upload)
- JSON file at project root: `gml_memory.json`
- Include in `.gitignore` if sharing code
- No personal data transmitted
- Only shared with code that accesses the file

```
# .gitignore
gml_memory.json
```

## Best Practices

1. **Save Periodically**: Memory auto-saves but you can save manually
   ```python
   gml.save_memory()
   ```

2. **Clean Up Old Memories**: Apply decay regularly
   ```python
   gml.apply_memory_decay(days=7)
   ```

3. **Use Entity Attributes**: Rich metadata helps recall
   ```python
   gml.update_entity_attribute(entity_id, "birthday", "2000-05-15")
   gml.update_entity_attribute(entity_id, "hobbies", "hiking, coding")
   ```

4. **Set Proper Confidence**: Manual memories should have moderate confidence
   ```python
   event.confidence = 0.85  # User explicitly told us
   ```

5. **Monitor Memory Stats**: Keep memory healthy
   ```python
   stats = gml.get_memory_stats()
   if stats['total_events'] > 1000:
       gml.apply_memory_decay()
   ```

## Troubleshooting

**Q: Bot doesn't remember something I told it**
- A: Check confidence score, may have decayed. Increase with "remember that..." command

**Q: Memory file is too large**
- A: Call `gml.apply_memory_decay()` to remove old memories

**Q: Entity not found during recall**
- A: Search by similar name using semantic search endpoint

**Q: Relationships not showing**
- A: Use `get_relationships()` to verify they exist

**Q: Memory lost after restart**
- A: Ensure `gml.save_memory()` is called periodically

## Performance Notes

- **Entities**: Supports thousands efficiently
- **Relationships**: Linear with entity count
- **Events**: Supports millions with periodic cleanup
- **Search**: O(n) with n = number of entities
- **Recall**: ~100ms for typical memory sizes

For 10,000+ entities, consider:
```python
gml.apply_memory_decay()  # Clean up weak memories
gml.consolidate_memories()  # Merge related memories
```

## Future Enhancements

Potential improvements:

1. **Vector Database**: Replace TF-IDF with neural embeddings (e.g., sentence-transformers)
2. **Graph Database**: Use Neo4j for relationship queries
3. **Multi-Agent Memory**: Share memories between AI agents
4. **Memory Summarization**: Auto-generate summaries of long interactions
5. **Temporal Reasoning**: Handle "Friday" vs specific dates
6. **Privacy Policies**: User-defined retention periods
7. **Memory Visualization**: Graph visualization of entities/relationships

## Examples

### Example 1: Learning About a Friend

```
Day 1:
User: "I met Alice today, she's an engineer"
Bot: Logs entity "Alice" with profession="engineer"

Day 2:
User: "What do I know about Alice?"
Bot: "Alice is an engineer"

Day 3:
User: "Remember Alice likes soccer"
Bot: Added attribute to Alice
```

### Example 2: Project Collaboration

```
User: "John and I are working on a machine learning project"
Bot: Creates entities John + User, relationship "works_with", logs event

Later...
User: "Who am I collaborating with?"
Bot: "You're working with John on a machine learning project"
```

### Example 3: Memory Search

```
User: "Tell me about engineering"
Bot: Searches all entities matching "engineering"
Bot: "I know Alice and Bob who are engineers. You're interested in AI and ML."
```

## APIs Summary

### REST API Endpoints
- `POST /api/memory/recall` - Semantic search
- `POST /api/memory/entity` - Add entity
- `GET /api/memory/entity/<query>` - Search entities
- `GET /api/memory/entity-info/<name>` - Full entity info
- `POST /api/memory/relationship` - Add relationship
- `POST /api/memory/event` - Log event
- `GET /api/memory/stats` - Statistics
- `POST /api/memory/save` - Save to disk
- `POST /api/memory/clear` - Clear all

### Python Methods
- `add_entity(name, type, attributes)` - Create entity
- `add_relationship(source_id, target_id, type, context)` - Create link
- `log_event(description, entities, type)` - Record interaction
- `recall(query, type)` - Semantic search
- `get_entity(id)` - Retrieve by ID
- `find_entity(name, type)` - Find by name
- `search_entities(query)` - Semantic search
- `save_memory()` - Persist to disk
- `apply_memory_decay(days)` - Forget old memories

## Conclusion

GML transforms your chatbot from a stateless system to one with **true intelligence**. By maintaining semantic memories of entities, relationships, and events, your bot can:

✓ Remember users across sessions  
✓ Understand complex relationships  
✓ Recall past conversations intelligently  
✓ Learn and adapt over time  
✓ Provide contextual, personalized responses  

**The future of AI is memory. GML makes it real.** 🧠📚

