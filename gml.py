"""
Gigzs Memory Layer (GML) - Semantic, Relational Memory System
Provides long-term contextual recall for AI through entity-relationship modeling
and vector embeddings for intelligent memory retrieval and decay.
"""

import json
import os
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import hashlib
from collections import defaultdict
import math


class VectorEmbedding:
    """Simple word-based vector embeddings using TF-IDF approach"""
    
    def __init__(self):
        self.vocab = set()
        self.word_to_idx = {}
        self.idf_scores = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization - split on whitespace and lowercase"""
        return text.lower().split()
    
    def update_vocab(self, texts: List[str]):
        """Build vocabulary and calculate IDF scores"""
        doc_freq = defaultdict(int)
        all_docs = len(texts)
        
        for text in texts:
            tokens = set(self._tokenize(text))
            for token in tokens:
                doc_freq[token] += 1
                self.vocab.add(token)
        
        # Calculate IDF scores
        for word in self.vocab:
            idf = math.log(all_docs / (1 + doc_freq[word]))
            self.idf_scores[word] = idf
        
        # Create word to index mapping
        self.word_to_idx = {word: idx for idx, word in enumerate(sorted(self.vocab))}
    
    def embed_text(self, text: str) -> np.ndarray:
        """Convert text to TF-IDF vector"""
        tokens = self._tokenize(text)
        vector = np.zeros(len(self.vocab))
        
        # Count term frequencies
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1
        
        # Build TF-IDF vector
        for word, freq in term_freq.items():
            if word in self.word_to_idx:
                idx = self.word_to_idx[word]
                tf = freq / len(tokens) if tokens else 0
                idf = self.idf_scores.get(word, 1)
                vector[idx] = tf * idf
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class Entity:
    """Represents an entity (person, place, concept) in memory"""
    
    def __init__(self, entity_id: str, name: str, entity_type: str, created_at: str = None):
        self.id = entity_id
        self.name = name
        self.type = entity_type  # "person", "place", "concept", etc.
        self.created_at = created_at or datetime.now().isoformat()
        self.attributes = {}  # Key-value pairs (e.g., {"age": 25, "profession": "engineer"})
        self.mentions = []  # List of timestamps when mentioned
        self.last_mentioned = self.created_at
        self.importance_score = 0.5  # 0-1, higher = more important
    
    def update_mention(self):
        """Update when entity is mentioned"""
        now = datetime.now().isoformat()
        self.mentions.append(now)
        self.last_mentioned = now
    
    def to_dict(self):
        """Convert entity to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'created_at': self.created_at,
            'last_mentioned': self.last_mentioned,
            'attributes': self.attributes,
            'mentions': self.mentions,
            'importance_score': self.importance_score
        }
    
    @staticmethod
    def from_dict(data: Dict):
        """Create entity from dictionary"""
        entity = Entity(data['id'], data['name'], data['type'], data.get('created_at'))
        entity.attributes = data.get('attributes', {})
        entity.mentions = data.get('mentions', [])
        entity.last_mentioned = data.get('last_mentioned', entity.created_at)
        entity.importance_score = data.get('importance_score', 0.5)
        return entity


class Relationship:
    """Represents a relationship between two entities"""
    
    def __init__(self, source_id: str, target_id: str, rel_type: str, 
                 context: str = "", created_at: str = None):
        self.source_id = source_id
        self.target_id = target_id
        self.type = rel_type  # "knows", "likes", "works_with", "located_in", etc.
        self.context = context
        self.created_at = created_at or datetime.now().isoformat()
        self.strength = 0.5  # 0-1, how strong is the relationship
        self.mentions = []  # When relationship was mentioned
        self.last_mentioned = self.created_at
    
    def update_mention(self):
        """Strengthen relationship with new mention"""
        now = datetime.now().isoformat()
        self.mentions.append(now)
        self.last_mentioned = now
        self.strength = min(1.0, self.strength + 0.1)  # Increase strength
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.type,
            'context': self.context,
            'created_at': self.created_at,
            'last_mentioned': self.last_mentioned,
            'strength': self.strength,
            'mentions': self.mentions
        }
    
    @staticmethod
    def from_dict(data: Dict):
        """Create from dictionary"""
        rel = Relationship(data['source_id'], data['target_id'], data['type'],
                          data.get('context', ''), data.get('created_at'))
        rel.strength = data.get('strength', 0.5)
        rel.mentions = data.get('mentions', [])
        rel.last_mentioned = data.get('last_mentioned', rel.created_at)
        return rel


class Event:
    """Represents a time-bound interaction or occurrence"""
    
    def __init__(self, event_id: str, description: str, involved_entities: List[str],
                 event_type: str = "interaction", timestamp: str = None):
        self.id = event_id
        self.description = description
        self.involved_entities = involved_entities
        self.type = event_type  # "interaction", "conversation", "achievement", etc.
        self.timestamp = timestamp or datetime.now().isoformat()
        self.context = {}  # Additional details
        self.importance = 0.5  # 0-1
        self.confidence = 0.8  # 0-1, how confident is this memory
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'involved_entities': self.involved_entities,
            'type': self.type,
            'timestamp': self.timestamp,
            'context': self.context,
            'importance': self.importance,
            'confidence': self.confidence
        }
    
    @staticmethod
    def from_dict(data: Dict):
        """Create from dictionary"""
        event = Event(data['id'], data['description'], data['involved_entities'],
                     data.get('type', 'interaction'), data.get('timestamp'))
        event.context = data.get('context', {})
        event.importance = data.get('importance', 0.5)
        event.confidence = data.get('confidence', 0.8)
        return event


class GigzsMemoryLayer:
    """
    Main semantic memory system for long-term AI recall.
    
    Features:
    - Entity management (people, places, concepts)
    - Relationship tracking with strength scoring
    - Event logging with temporal information
    - Vector embeddings for semantic search
    - Memory decay and selective forgetting
    - Confidence scoring
    """
    
    def __init__(self, storage_file: str = "gml_memory.json"):
        self.storage_file = storage_file
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.events: Dict[str, Event] = {}
        self.embedding_model = VectorEmbedding()
        self.memory_decay_factor = 0.99  # Daily decay
        self.memory_decay_threshold = 0.1  # Below this, forget memory
        
        # Load existing memory
        self._load_memory()
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        timestamp = datetime.now().isoformat()
        hash_val = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"{prefix}_{hash_val}"
    
    # ==================== Entity Management ====================
    
    def add_entity(self, name: str, entity_type: str, attributes: Dict = None) -> str:
        """
        Add a new entity to memory.
        
        Args:
            name: Entity name (e.g., "Alice", "New York")
            entity_type: Type (e.g., "person", "place", "concept")
            attributes: Optional dict of attributes
        
        Returns:
            Entity ID
        """
        entity_id = self._generate_id(entity_type.lower())
        entity = Entity(entity_id, name, entity_type)
        
        if attributes:
            entity.attributes = attributes
        
        self.entities[entity_id] = entity
        self._update_embeddings()
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve entity by ID"""
        entity = self.entities.get(entity_id)
        if entity:
            entity.update_mention()
        return entity
    
    def find_entity(self, name: str, entity_type: str = None) -> Optional[str]:
        """
        Find entity by name and optional type.
        Returns entity ID or None.
        """
        for ent_id, entity in self.entities.items():
            if entity.name.lower() == name.lower():
                if entity_type is None or entity.type == entity_type:
                    entity.update_mention()
                    return ent_id
        return None
    
    def search_entities(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Search entities by semantic similarity.
        Returns list of (entity_id, similarity_score) tuples.
        """
        if not self.entities:
            return []
        
        query_vector = self.embedding_model.embed_text(query)
        scores = []
        
        for ent_id, entity in self.entities.items():
            entity_vector = self.embedding_model.embed_text(entity.name + " " + entity.type)
            similarity = self.embedding_model.cosine_similarity(query_vector, entity_vector)
            if similarity > 0.3:  # Threshold
                scores.append((ent_id, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
    
    def update_entity_attribute(self, entity_id: str, key: str, value):
        """Update entity attribute"""
        if entity_id in self.entities:
            self.entities[entity_id].attributes[key] = value
            self.entities[entity_id].update_mention()
    
    # ==================== Relationship Management ====================
    
    def add_relationship(self, source_id: str, target_id: str, rel_type: str,
                        context: str = "") -> bool:
        """
        Add relationship between two entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            rel_type: Relationship type (e.g., "knows", "likes")
            context: Optional context about relationship
        
        Returns:
            True if successful
        """
        if source_id not in self.entities or target_id not in self.entities:
            return False
        
        # Check if relationship already exists
        for rel in self.relationships:
            if (rel.source_id == source_id and rel.target_id == target_id and
                rel.type == rel_type):
                rel.update_mention()
                return True
        
        # Add new relationship
        rel = Relationship(source_id, target_id, rel_type, context)
        self.relationships.append(rel)
        return True
    
    def get_relationships(self, entity_id: str, direction: str = "all") -> List[Relationship]:
        """
        Get relationships for an entity.
        
        Args:
            entity_id: Entity ID
            direction: "all", "outgoing", "incoming"
        
        Returns:
            List of relationships
        """
        rels = []
        for rel in self.relationships:
            if direction in ("all", "outgoing") and rel.source_id == entity_id:
                rels.append(rel)
            elif direction in ("all", "incoming") and rel.target_id == entity_id:
                rels.append(rel)
        
        # Sort by strength (descending)
        rels.sort(key=lambda r: r.strength, reverse=True)
        return rels
    
    # ==================== Event Management ====================
    
    def log_event(self, description: str, involved_entities: List[str],
                  event_type: str = "interaction") -> str:
        """
        Log an event in memory.
        
        Args:
            description: Event description
            involved_entities: List of entity IDs involved
            event_type: Type of event
        
        Returns:
            Event ID
        """
        event_id = self._generate_id("event")
        event = Event(event_id, description, involved_entities, event_type)
        self.events[event_id] = event
        
        # Update entities to mark they were involved
        for ent_id in involved_entities:
            if ent_id in self.entities:
                self.entities[ent_id].update_mention()
        
        self._update_embeddings()
        return event_id
    
    def get_events_for_entity(self, entity_id: str, limit: int = 10) -> List[Event]:
        """Get events involving an entity"""
        events = [e for e in self.events.values() if entity_id in e.involved_entities]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def search_events(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Search events by semantic similarity"""
        if not self.events:
            return []
        
        query_vector = self.embedding_model.embed_text(query)
        scores = []
        
        for evt_id, event in self.events.items():
            event_vector = self.embedding_model.embed_text(event.description)
            similarity = self.embedding_model.cosine_similarity(query_vector, event_vector)
            if similarity > 0.3:
                scores.append((evt_id, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
    
    # ==================== Memory Recall & Query ====================
    
    def recall(self, query: str, recall_type: str = "all") -> Dict:
        """
        Recall memories based on query.
        
        Args:
            query: Recall query
            recall_type: "entities", "events", "all"
        
        Returns:
            Dict with recalled memories
        """
        result = {
            'query': query,
            'entities': [],
            'events': [],
            'relationships': []
        }
        
        if recall_type in ("entities", "all"):
            entities = self.search_entities(query)
            for ent_id, score in entities:
                entity = self.entities[ent_id]
                result['entities'].append({
                    'id': ent_id,
                    'name': entity.name,
                    'type': entity.type,
                    'similarity': score,
                    'attributes': entity.attributes
                })
                
                # Get related relationships
                rels = self.get_relationships(ent_id)
                for rel in rels[:3]:  # Top 3
                    target = self.entities.get(rel.target_id)
                    result['relationships'].append({
                        'from': entity.name,
                        'to': target.name if target else 'Unknown',
                        'type': rel.type,
                        'strength': rel.strength
                    })
        
        if recall_type in ("events", "all"):
            events = self.search_events(query)
            for evt_id, score in events:
                event = self.events[evt_id]
                result['events'].append({
                    'id': evt_id,
                    'description': event.description,
                    'type': event.type,
                    'timestamp': event.timestamp,
                    'similarity': score,
                    'confidence': event.confidence
                })
        
        return result
    
    def recall_about_entity(self, entity_name: str) -> Dict:
        """Recall all memories about a specific entity"""
        entity_id = self.find_entity(entity_name)
        
        if not entity_id:
            return {'error': f'Entity "{entity_name}" not found'}
        
        entity = self.entities[entity_id]
        events = self.get_events_for_entity(entity_id)
        relationships = self.get_relationships(entity_id)
        
        return {
            'entity': {
                'id': entity_id,
                'name': entity.name,
                'type': entity.type,
                'attributes': entity.attributes,
                'last_mentioned': entity.last_mentioned
            },
            'events': [e.to_dict() for e in events],
            'relationships': [r.to_dict() for r in relationships]
        }
    
    # ==================== Memory Decay & Management ====================
    
    def apply_memory_decay(self, days: int = 1):
        """
        Apply temporal decay to memories.
        Older, less important memories decay faster.
        """
        now = datetime.now()
        decay_rate = math.pow(self.memory_decay_factor, days)
        
        for entity in list(self.entities.values()):
            # Decay importance based on time since last mention
            if entity.last_mentioned:
                last_mention = datetime.fromisoformat(entity.last_mentioned)
                days_since = (now - last_mention).days
                entity.importance_score *= math.pow(self.memory_decay_factor, days_since)
            
            # Remove very weak memories
            if entity.importance_score < self.memory_decay_threshold:
                del self.entities[entity.id]
        
        # Decay relationships
        self.relationships = [
            r for r in self.relationships
            if not (r.strength < self.memory_decay_threshold and
                   (now - datetime.fromisoformat(r.last_mentioned)).days > 30)
        ]
        
        # Decay events
        for evt_id in list(self.events.keys()):
            event = self.events[evt_id]
            if (now - datetime.fromisoformat(event.timestamp)).days > 365:
                del self.events[evt_id]
    
    def consolidate_memories(self):
        """Summarize and consolidate related memories"""
        # Group entities by type
        entities_by_type = defaultdict(list)
        for ent_id, entity in self.entities.items():
            entities_by_type[entity.type].append((ent_id, entity))
        
        return {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'total_events': len(self.events),
            'entities_by_type': {
                etype: [(e.name, e.importance_score) for _, e in entities]
                for etype, entities in entities_by_type.items()
            }
        }
    
    # ==================== Persistence ====================
    
    def _update_embeddings(self):
        """Update vector embeddings for all texts"""
        texts = (
            [e.name for e in self.entities.values()] +
            [e.description for e in self.events.values()]
        )
        if texts:
            self.embedding_model.update_vocab(texts)
    
    def save_memory(self):
        """Save memory to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'entities': {eid: e.to_dict() for eid, e in self.entities.items()},
            'relationships': [r.to_dict() for r in self.relationships],
            'events': {eid: e.to_dict() for eid, e in self.events.items()}
        }
        
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def _load_memory(self):
        """Load memory from file"""
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            # Load entities
            for eid, edata in data.get('entities', {}).items():
                self.entities[eid] = Entity.from_dict(edata)
            
            # Load relationships
            for rdata in data.get('relationships', []):
                self.relationships.append(Relationship.from_dict(rdata))
            
            # Load events
            for eid, edata in data.get('events', {}).items():
                self.events[eid] = Event.from_dict(edata)
            
            self._update_embeddings()
        except Exception as e:
            print(f"Error loading memory: {e}")
    
    # ==================== Utility Methods ====================
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'total_events': len(self.events),
            'vocabulary_size': len(self.embedding_model.vocab),
            'storage_file': self.storage_file,
            'last_saved': 'N/A'  # Update when saving
        }
    
    def clear_memory(self):
        """Clear all memories"""
        self.entities.clear()
        self.relationships.clear()
        self.events.clear()
        self.embedding_model = VectorEmbedding()


# Example usage and testing
if __name__ == "__main__":
    # Initialize GML
    gml = GigzsMemoryLayer()
    
    print("=== Gigzs Memory Layer (GML) Demo ===\n")
    
    # Add some entities
    print("1. Adding entities...")
    alice_id = gml.add_entity("Alice", "person", {"age": 25, "profession": "engineer"})
    bob_id = gml.add_entity("Bob", "person", {"age": 30, "profession": "designer"})
    nyc_id = gml.add_entity("New York", "place")
    
    # Add relationships
    print("2. Creating relationships...")
    gml.add_relationship(alice_id, bob_id, "knows", "met at conference")
    gml.add_relationship(alice_id, nyc_id, "located_in")
    
    # Log events
    print("3. Logging events...")
    event1 = gml.log_event(
        "Alice and Bob worked on a machine learning project together",
        [alice_id, bob_id],
        "collaboration"
    )
    
    # Recall memories
    print("4. Recalling memories...")
    recall = gml.recall("Who did I meet?")
    print(f"Recall result: {json.dumps(recall, indent=2)}")
    
    # Recall about entity
    print("\n5. Recalling about Alice...")
    about_alice = gml.recall_about_entity("Alice")
    print(f"About Alice: {json.dumps(about_alice, indent=2)}")
    
    # Save memory
    print("\n6. Saving memory to disk...")
    gml.save_memory()
    
    # Get stats
    print("\n7. Memory statistics:")
    stats = gml.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
