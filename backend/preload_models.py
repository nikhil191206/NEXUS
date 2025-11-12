"""
Pre-load transformer models to download them before user uploads documents.
This ensures the first document upload is fast.
"""

from transformers import pipeline
import sys

def preload_models():
    """Download and initialize transformer models."""
    try:
        print("Starting model download...", flush=True)

        # Load NER model (BERT)
        print("Step 1/2: Downloading BERT NER model (~200MB)...", flush=True)
        ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        print("✓ BERT model loaded successfully", flush=True)

        # Load T5 model for relation extraction
        print("Step 2/2: Downloading T5 model (~150MB)...", flush=True)
        relation_pipeline = pipeline(
            "text2text-generation",
            model="google/flan-t5-small"
        )
        print("✓ T5 model loaded successfully", flush=True)

        # Test the models
        print("Testing models...", flush=True)
        test_text = "Machine Learning is a field of AI."
        ner_pipeline(test_text)
        relation_pipeline("test")

        print("✓ All models ready!", flush=True)
        return True

    except Exception as e:
        print(f"✗ Error loading models: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = preload_models()
    sys.exit(0 if success else 1)
