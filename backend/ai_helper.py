from transformers import pipeline
import re
from typing import List, Tuple, Set

class TransformerHelper:
    def __init__(self):
        self.nodes = set()
        self.edges = []
        print("Loading transformer models...")
        print("This may take a minute on first run (downloading models)...")
        
        try:
            self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
            print("SUCCESS - Loaded NER model (BERT)")
        except Exception as e:
            print(f"ERROR - Could not load NER model: {e}")
            self.ner_pipeline = None
        
        try:
            self.relation_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
            print("SUCCESS - Loaded relation extraction model (T5)")
        except Exception as e:
            print(f"ERROR - Could not load relation model: {e}")
            self.relation_pipeline = None

    def extract_entities(self, text: str) -> Set[str]:
        entities = set()
        if self.ner_pipeline:
            print("   Extracting entities with BERT NER...")
            ner_results = self.ner_pipeline(text)
            for entity in ner_results:
                entity_text = entity['word'].strip().replace(' ##', '')
                if len(entity_text) > 2:
                    entities.add(entity_text)
                    print(f"      Found: {entity_text} ({entity['entity_group']})")
        
        capitalized_pattern = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b'
        for match in re.finditer(capitalized_pattern, text):
            term = match.group().strip()
            if len(term) > 2 and term not in ['The', 'This', 'That', 'A', 'An']:
                entities.add(term)
        
        acronym_pattern = r'\b[A-Z]{2,}\b'
        for match in re.finditer(acronym_pattern, text):
            entities.add(match.group())
        
        return entities

    def extract_relationships_pattern(self, text: str, entities: Set[str]) -> List[Tuple[str, str, str]]:
        relationships = []
        patterns = [
            (r'(\w+(?:\s+\w+)*)\s+is\s+a\s+type\s+of\s+(\w+(?:\s+\w+)*)', 'is_type_of'),
            (r'(\w+(?:\s+\w+)*)\s+is\s+a\s+subset\s+of\s+(\w+(?:\s+\w+)*)', 'is_subset_of'),
            (r'(\w+(?:\s+\w+)*)\s+is\s+an?\s+(\w+(?:\s+\w+)*)', 'is_a'),
            (r'(\w+(?:\s+\w+)*)\s+uses\s+(\w+(?:\s+\w+)*)', 'uses'),
            (r'(\w+(?:\s+\w+)*)\s+prevents\s+(\w+(?:\s+\w+)*)', 'prevents'),
            (r'(\w+(?:\s+\w+)*)\s+improves\s+(\w+(?:\s+\w+)*)', 'improves'),
            (r'(\w+(?:\s+\w+)*)\s+revolutionized\s+(\w+(?:\s+\w+)*)', 'revolutionized'),
        ]
        
        for pattern, relation in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                source = match.group(1).strip()
                target = match.group(2).strip()
                source_match = self._find_entity(source, entities)
                target_match = self._find_entity(target, entities)
                if source_match and target_match:
                    relationships.append((source_match, relation, target_match))
                    print(f"      Pattern: {source_match} --[{relation}]--> {target_match}")
        
        return relationships

    def _find_entity(self, text: str, entities: Set[str]) -> str:
        if text in entities:
            return text
        for entity in entities:
            if text.lower() in entity.lower() or entity.lower() in text.lower():
                return entity
        return None

    def process_document(self, text: str, output_file: str):
        print("\n" + "="*80)
        print("TRANSFORMER AI EXTRACTION")
        print("="*80)
        print("\n1. Extracting entities with BERT...")
        entities = self.extract_entities(text)
        self.nodes = entities
        print(f"\nSUCCESS - Found {len(entities)} entities")
        print("\n2. Extracting relationships...")
        relationships = self.extract_relationships_pattern(text, entities)
        print(f"\nSUCCESS - Found {len(relationships)} relationships")
        unique_relationships = list(set(relationships))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for node in sorted(self.nodes):
                f.write(f"NODE: {node}\n")
            for source, relation, target in unique_relationships:
                f.write(f"EDGE: {source}|{relation}|{target}\n")
        
        print("\n" + "="*80)
        print(f"SUCCESS - Extraction complete!")
        print(f"SUCCESS - {len(self.nodes)} nodes, {len(unique_relationships)} relationships")
        print(f"SUCCESS - Output: {output_file}")
        print("="*80)

def process_text_file(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    helper = TransformerHelper()
    helper.process_document(text, output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ai_helper.py <input_file> <output_file>")
        sys.exit(1)
    print("\n" + "="*80)
    print("NEXUS AI HELPER - Transformer Extraction")
    print("="*80)
    process_text_file(sys.argv[1], sys.argv[2])