"""
Pure Transformer AI Helper - No SpaCy needed!
Uses only transformers library for extraction.
"""

from transformers import pipeline
import re
from typing import List, Tuple, Set

class TransformerOnlyHelper:
    """
    AI Helper using ONLY transformers - no SpaCy dependency.
    Perfect when you have SpaCy compatibility issues.
    """

    def __init__(self):
        self.nodes = set()
        self.edges = []

        print("Loading transformer models...")
        print("This may take a minute on first run (downloading models)...")

        # Load NER model for entity extraction
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            print("✓ Loaded NER model (BERT)")
        except Exception as e:
            print(f"⚠ Could not load NER model: {e}")
            self.ner_pipeline = None

        # Load text generation for relation extraction
        try:
            self.relation_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-small"
            )
            print("✓ Loaded relation extraction model (T5)")
        except Exception as e:
            print(f"⚠ Could not load relation model: {e}")
            self.relation_pipeline = None

    def extract_entities_transformer(self, text: str) -> Set[str]:
        """Extract entities using transformer NER."""
        entities = set()

        if self.ner_pipeline:
            print("   Extracting entities with BERT NER...")
            # Run NER
            ner_results = self.ner_pipeline(text)

            for entity in ner_results:
                entity_text = entity['word'].strip()
                # Clean up BERT tokenization artifacts
                entity_text = entity_text.replace(' ##', '')
                if len(entity_text) > 2:
                    entities.add(entity_text)
                    print(f"      Found: {entity_text} ({entity['entity_group']})")

        # Also extract capitalized phrases (technical terms)
        capitalized_pattern = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b'
        for match in re.finditer(capitalized_pattern, text):
            term = match.group().strip()
            if len(term) > 2 and term not in ['The', 'This', 'That', 'A', 'An']:
                entities.add(term)

        # Extract acronyms and compounds
        acronym_pattern = r'\b[A-Z]{2,}\b'
        for match in re.finditer(acronym_pattern, text):
            entities.add(match.group())

        return entities

    def extract_relationships_transformer(self, text: str, entities: List[str]) -> List[Tuple[str, str, str]]:
        """Extract relationships using T5 transformer."""
        if not self.relation_pipeline:
            return self._extract_relationships_patterns(text, entities)

        relationships = []
        print("   Extracting relationships with T5...")

        # Limit to avoid too many API calls
        entity_list = list(entities)[:15]  # Top 15 entities

        for i, ent1 in enumerate(entity_list):
            for ent2 in entity_list[i+1:]:
                # Create prompt for T5
                prompt = f"Describe the relationship between '{ent1}' and '{ent2}' in one short phrase. If no relationship, say 'none'.\n\nText: {text[:500]}"

                try:
                    result = self.relation_pipeline(
                        prompt,
                        max_length=30,
                        min_length=3,
                        num_return_sequences=1
                    )[0]['generated_text']

                    # Parse result
                    result = result.lower().strip()

                    if 'none' not in result and len(result) > 3:
                        # Clean up the relation
                        relation = result.replace(ent1.lower(), '').replace(ent2.lower(), '').strip()
                        relation = re.sub(r'^(is |are |was |were )', '', relation)
                        relation = relation.replace(' ', '_')

                        if relation:
                            relationships.append((ent1, relation, ent2))
                            print(f"      T5: {ent1} --[{relation}]--> {ent2}")

                except Exception as e:
                    print(f"      Error processing {ent1}-{ent2}: {e}")
                    continue

        return relationships

    def _extract_relationships_patterns(self, text: str, entities: Set[str]) -> List[Tuple[str, str, str]]:
        """Fallback pattern-based extraction if transformer fails."""
        relationships = []

        patterns = [
            (r'(\w+(?:\s+\w+)*)\s+is\s+a\s+type\s+of\s+(\w+(?:\s+\w+)*)', 'is_type_of'),
            (r'(\w+(?:\s+\w+)*)\s+is\s+an?\s+(\w+(?:\s+\w+)*)', 'is_a'),
            (r'(\w+(?:\s+\w+)*)\s+uses\s+(\w+(?:\s+\w+)*)', 'uses'),
            (r'(\w+(?:\s+\w+)*)\s+prevents\s+(\w+(?:\s+\w+)*)', 'prevents'),
            (r'(\w+(?:\s+\w+)*)\s+improves\s+(\w+(?:\s+\w+)*)', 'improves'),
            (r'(\w+(?:\s+\w+)*)\s+enables\s+(\w+(?:\s+\w+)*)', 'enables'),
            (r'(\w+(?:\s+\w+)*)\s+revolutionized\s+(\w+(?:\s+\w+)*)', 'revolutionized'),
        ]

        for pattern, relation in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                source = match.group(1).strip()
                target = match.group(2).strip()

                # Check if entities match
                source_match = self._find_entity(source, entities)
                target_match = self._find_entity(target, entities)

                if source_match and target_match:
                    relationships.append((source_match, relation, target_match))

        return relationships

    def _find_entity(self, text: str, entities: Set[str]) -> str:
        """Find matching entity."""
        if text in entities:
            return text

        for entity in entities:
            if text.lower() in entity.lower() or entity.lower() in text.lower():
                return entity

        return None

    def process_document(self, text: str, output_file: str):
        """Process document with transformers."""
        print("\n" + "="*80)
        print("TRANSFORMER-ONLY AI EXTRACTION (No SpaCy!)")
        print("="*80)

        # Extract entities
        print("\n1. Extracting entities with BERT...")
        entities = self.extract_entities_transformer(text)
        self.nodes = entities
        print(f"\n✓ Found {len(entities)} entities")

        # Extract relationships
        print("\n2. Extracting relationships with T5...")
        relationships = self.extract_relationships_transformer(text, list(entities))

        # Add pattern-based relationships as supplement
        print("\n3. Adding pattern-based relationships...")
        pattern_relationships = self._extract_relationships_patterns(text, entities)
        relationships.extend(pattern_relationships)

        print(f"\n✓ Found {len(relationships)} relationships")

        # Remove duplicates
        unique_relationships = list(set(relationships))

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for node in sorted(self.nodes):
                f.write(f"NODE: {node}\n")

            for source, relation, target in unique_relationships:
                f.write(f"EDGE: {source}|{relation}|{target}\n")

        print("\n" + "="*80)
        print(f"✓ Extraction complete!")
        print(f"✓ {len(self.nodes)} nodes, {len(unique_relationships)} relationships")
        print(f"✓ Output: {output_file}")
        print("="*80)


def process_text_file(input_file: str, output_file: str):
    """Main function."""
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    helper = TransformerOnlyHelper()
    helper.process_document(text, output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python ai_helper_transformer_only.py <input_file> <output_file>")
        print("\nThis uses ONLY transformers - NO SpaCy needed!")
        print("Perfect when you have SpaCy compatibility issues.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  TRANSFORMER-ONLY AI HELPER                                  ║
║                                                                              ║
║  Uses BERT for NER + T5 for relation extraction                             ║
║  No SpaCy dependency - works when SpaCy has issues!                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    process_text_file(input_file, output_file)
