# download_musique_3plus_hops.py

from datasets import load_dataset
import json
from pathlib import Path
import yaml

def download_musique_3plus_hops():
    """
    Download MusiQue dataset and filter for questions requiring 3+ hops.
    MusiQue is specifically designed to require genuine multi-hop reasoning.
    """
    
    print("Downloading MusiQue dataset from Hugging Face...")
    print("Dataset: bdsaglam/musique")
    print("This may take a few minutes...\n")
    
    # Load the dataset - use answerable subset (has ground truth)
    dataset = load_dataset("bdsaglam/musique", "answerable")
    
    # Use validation set (smaller, has answers)
    data = dataset['validation']
    
    print(f"✓ Downloaded {len(data)} answerable questions\n")
    
    # Filter for 3+ hops
    multi_hop_3plus = []
    
    for item in data:
        # question_decomposition shows the reasoning steps
        decomposition = item.get('question_decomposition', [])
        num_hops = len(decomposition)
        
        # Filter for 3+ hops (so 3 or 4 hops)
        if num_hops >= 3:
            multi_hop_3plus.append(item)
    
    print(f"Filtered to {len(multi_hop_3plus)} questions requiring 3+ hops")
    
    # Show distribution
    hop_distribution = {}
    for item in multi_hop_3plus:
        num_hops = len(item.get('question_decomposition', []))
        hop_distribution[num_hops] = hop_distribution.get(num_hops, 0) + 1
    
    print(f"\nHop distribution:")
    for hops, count in sorted(hop_distribution.items()):
        print(f"  {hops}-hop: {count} questions")
    
    # Use first 500 questions to get medium-sized KB
    subset = multi_hop_3plus[:500]
    
    # Extract documents from paragraphs
    documents = {}
    for item in subset:
        for para in item['paragraphs']:
            title = para['title']
            text = para['paragraph_text']
            is_supporting = para.get('is_supporting', False)
            
            if title not in documents and len(text.strip()) > 0:
                doc_id = f"MUSIQUE-{len(documents):05d}"
                documents[title] = {
                    'doc_id': doc_id,
                    'title': title,
                    'text': text,
                    'is_supporting': is_supporting
                }
    
    print(f"\nExtracted {len(documents)} unique documents")
    
    # Create markdown files
    output_dir = Path("data/musique")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    title_to_id = {}
    for title, doc in documents.items():
        title_to_id[title] = doc['doc_id']
        
        filepath = output_dir / f"{doc['doc_id']}.md"
        
        frontmatter = {
            'doc_id': doc['doc_id'],
            'doc_type': ['encyclopedia', 'factual'],
            'category': 'wikipedia',
            'title': doc['title'],
            'date': '2024-01-01'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
            f.write("---\n\n")
            f.write(f"# {doc['title']}\n\n")
            f.write(doc['text'])
    
    print(f"✓ Created {len(documents)} markdown files\n")
    
    # Create test queries (only 3+ hops)
    test_queries = []
    for item in subset[:100]:  # 100 test queries
        
        # Extract supporting paragraphs
        expected_sources = []
        for para in item['paragraphs']:
            if para.get('is_supporting', False):
                title = para['title']
                if title in title_to_id:
                    doc_id = title_to_id[title]
                    if doc_id not in expected_sources:
                        expected_sources.append(doc_id)
        
        # Get decomposition steps
        decomposition = item.get('question_decomposition', [])
        num_hops = len(decomposition)
        
        test_queries.append({
            'query': item['question'],
            'expected_answer': item['answer'],
            'expected_sources': expected_sources,
            'expected_topics': item['answer'].lower().split()[:5],
            'query_type': 'multi_part',
            'difficulty': 'hard',
            'notes': f"MusiQue: Requires {num_hops} hops",
            'decomposition_steps': [step['question'] for step in decomposition],
            'num_hops': num_hops
        })
    
    print(f"Created {len(test_queries)} test queries (all 3+ hops)")
    
    # Save
    with open('evaluation/musique_test_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(test_queries, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("MusiQue 3+ Hops Dataset Setup Complete!")
    print("="*70)
    print(f"Documents:    {len(documents)}")
    print(f"Test queries: {len(test_queries)}")
    print(f"Min hops:     3")
    print(f"Max hops:     {max(q['num_hops'] for q in test_queries)}")
    print("="*70)
    
    # Show example
    if test_queries:
        print(f"\n{'='*70}")
        print("Example 3+ Hop Question:")
        print("="*70)
        example = test_queries[0]
        print(f"Question: {example['query']}")
        print(f"Answer:   {example['expected_answer']}")
        print(f"Hops:     {example['num_hops']}")
        print(f"\nDecomposition steps:")
        for i, step in enumerate(example['decomposition_steps'], 1):
            print(f"  {i}. {step}")
        print(f"\nRequired docs: {len(example['expected_sources'])}")
    
    print(f"\n{'='*70}")
    
    return len(documents), len(test_queries)

if __name__ == "__main__":
    import subprocess
    import sys
    
    # Check if datasets is installed
    try:
        import datasets
        print("✓ datasets library found\n")
    except ImportError:
        print("Installing datasets library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets"])
        print("\n✓ Installation complete!")
        print("Please run the script again.\n")
        sys.exit(0)
    
    download_musique_3plus_hops()