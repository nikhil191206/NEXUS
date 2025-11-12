import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import google.generativeai as genai
from typing import List, Tuple, Set
import warnings
import re

warnings.filterwarnings('ignore')

# This is the "magic". A carefully crafted prompt to force Gemini
# to return *only* the data in the format your C-Core understands.
SYSTEM_PROMPT = """
You are a highly intelligent knowledge graph extraction engine. Your task is to read the user-provided text and extract all significant entities and their relationships.

You MUST format your entire output ONLY as a plain text list of NODE and EDGE definitions, exactly as shown below.
- First, list all unique nodes.
- Then, list all edges that connect them.

The format is:
NODE: [Entity Name]
EDGE: [Source Entity]|[Relationship Type]|[Target Entity]

Here is an example:
Text: "Python is a language used for data science. Pandas is built on NumPy."
Your Output:
NODE: Python
NODE: language
NODE: data science
NODE: Pandas
NODE: NumPy
EDGE: Python|is a|language
EDGE: Python|used for|data science
EDGE: Pandas|is built on|NumPy

Do not include any other text, explanation, or markdown like "Here is the output:" or "```".
Your response must be 100% in this format.
"""

class GeminiHelper:
    def __init__(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.generation_config = genai.GenerationConfig(
                temperature=0.0, # Set to 0.0 for most deterministic, factual output
            )
            print("Gemini model loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to initialize Gemini model: {e}")
            self.model = None

    def process_document(self, text: str, output_file: str):
        if not self.model:
            print("ERROR: Gemini model not available. Cannot process document.")
            return

        print("Processing document with Gemini API...")
        
        # Combine the system prompt with the user's text
        full_prompt = f"{SYSTEM_PROMPT}\n\nHere is the text to process:\n\n{text}"

        try:
            # Send the request to the API
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            # The 'response.text' should be the perfectly formatted graph data
            graph_data = response.text.strip()
            
            # A quick validation to make sure the output isn't garbage
            if not graph_data.startswith("NODE:") and not graph_data.startswith("EDGE:"):
                print(f"WARNING: Gemini output did not seem to follow format. Output was:\n{graph_data}")
                # You could try to clean it, but for now we'll just write it
            
            # Write the clean data to the output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(graph_data)
                
            print(f"Graph file created at {output_file}")
            # Log a small part of the output
            print("\n--- Gemini Output (First 5 lines) ---")
            print('\n'.join(graph_data.split('\n')[:5]))
            print("--------------------------------------")

        except Exception as e:
            print(f"ERROR: Failed to generate content with Gemini: {e}")
            # Write an empty file so the C-Core doesn't crash
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("") # Write empty
            

def process_text_file(input_file: str, output_file: str):
    # 1. Get the API Key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        print("Please set the variable before running.")
        return

    # 2. Read the input text
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
            if not text.strip():
                print("Input file is empty. Skipping.")
                return
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {input_file}")
        return

    # 3. Process with the helper
    helper = GeminiHelper(api_key=api_key)
    helper.process_document(text, output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ai_helper.py <input_file> <output_file>")
        sys.exit(1)
    
    print(f"Processing {sys.argv[1]} -> {sys.argv[2]}")
    process_text_file(sys.argv[1], sys.argv[2])
    print("Processing complete.")