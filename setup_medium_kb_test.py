# setup_hotpotqa_medium_test.py

import json
import requests
from pathlib import Path
import yaml  # Add this import

def safe_yaml_string(value):
    """
    Safely format a string for YAML.
    Quotes it if it contains special characters.
    """
    if not value:
        return '""'
    
    # Characters that need quoting in YAML
    needs_quoting = [':', '#', '@', '&', '*', '!', '|', '>', "'", '"', '%', '[', ']', '{', '}']
    
    if any(char in value for char in needs_quoting):
        # Use double quotes and escape any internal quotes
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    
    return value

def setup_hotpotqa_medium_test():
    """
    Setup medium KB test with HotpotQA
    """
    
    # Download
    url = "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json"
    print("Downloading HotpotQA...")
    data = requests.get(url).json()
    
    # Take first 2000 questions
    subset = data[:2000]
    
    # Extract unique documents
    documents = {}
    for item in subset:
        for doc_title, doc_sentences in item['context']:
            if doc_title not in documents:
                doc_id = f"WIKI-{len(documents):05d}"
                documents[doc_title] = {
                    'doc_id': doc_id,
                    'title': doc_title,
                    'text': ' '.join(doc_sentences)
                }
    
    print(f"Extracted {len(documents)} documents (medium KB size)")
    
    # Create markdown files
    output_dir = Path("data/hotpotqa")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    title_to_id = {}
    for title, doc in documents.items():
        title_to_id[title] = doc['doc_id']
        
        filepath = output_dir / f"{doc['doc_id']}.md"
        with open(filepath, 'w') as f:
            f.write(f"---\n")
            f.write(f"doc_id: {doc['doc_id']}\n")
            f.write(f"doc_type:\n")
            f.write(f"  - encyclopedia\n")
            f.write(f"  - factual\n")
            f.write(f"category: wikipedia\n")
            f.write(f"title: {safe_yaml_string(doc['title'])}\n")
            f.write(f"date: 2024-01-01\n")
            f.write(f"---\n\n")
            f.write(f"# {doc['title']}\n\n")
            f.write(doc['text'])
    
    # Create test queries (rest of the code...)
    test_queries = []
    for item in subset[:100]:
        expected_sources = []
        for title, sent_id in item['supporting_facts']:
            if title in title_to_id:
                doc_id = title_to_id[title]
                if doc_id not in expected_sources:
                    expected_sources.append(doc_id)
        
        is_multi_hop = len(expected_sources) >= 2
        
        test_queries.append({
            'query': item['question'],
            'expected_answer': item['answer'],
            'expected_sources': expected_sources,
            'expected_topics': item['answer'].lower().split()[:3],
            'query_type': 'multi_part' if is_multi_hop else 'complex',
            'difficulty': 'hard' if is_multi_hop else 'medium',
            'notes': f"HotpotQA level: {item['level']}"
        })
    
    # Save test dataset
    output_file = "evaluation/hotpotqa_test_dataset.json"
    with open(output_file, 'w') as f:
        json.dump(test_queries, f, indent=2)
    
    print(f"\nSetup complete!")
    print(f"Documents: {len(documents)} (medium KB)")
    print(f"Test queries: {len(test_queries)}")
    print(f"Test file: {output_file}")
    
    return len(documents), len(test_queries)

if __name__ == "__main__":
    setup_hotpotqa_medium_test()