import argparse
import json
import csv
import sys
import os

# Add src to python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from scorer import score_candidate
from reasoning_engine import generate_reasoning

def process_candidates(candidates_path, limit=100):
    scored_candidates = []
    
    # Check if gzip or regular jsonl
    if candidates_path.endswith('.gz'):
        import gzip
        open_func = gzip.open
        mode = 'rt'
    else:
        open_func = open
        mode = 'r'
        
    print(f"Reading and scoring candidates from {candidates_path}...")
    
    if candidates_path.endswith('.json'):
        with open_func(candidates_path, mode, encoding='utf-8') as f:
            candidates_list = json.load(f)
        for i, candidate in enumerate(candidates_list):
            try:
                score, sub_scores, is_honeypot = score_candidate(candidate)
                if not is_honeypot:
                    scored_candidates.append({
                        'candidate_id': candidate.get('candidate_id'),
                        'score': score,
                        'sub_scores': sub_scores,
                        'candidate_data': candidate
                    })
            except Exception as e:
                print(f"Error processing candidate at index {i}: {e}")
    else:
        with open_func(candidates_path, mode, encoding='utf-8') as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                    
                try:
                    candidate = json.loads(line)
                    score, sub_scores, is_honeypot = score_candidate(candidate)
                    
                    if not is_honeypot:
                        scored_candidates.append({
                            'candidate_id': candidate.get('candidate_id'),
                            'score': score,
                            'sub_scores': sub_scores,
                            'candidate_data': candidate
                        })
                except Exception as e:
                    print(f"Error parsing candidate at line {i}: {e}")
                
    # Sort candidates by rounded score descending, then by candidate_id ascending for tie-breaks
    print(f"Sorting {len(scored_candidates)} valid candidates...")
    scored_candidates.sort(key=lambda x: (-round(x['score'], 4), x['candidate_id']))
    
    # Get top 100
    top_k = scored_candidates[:limit]
    
    # Generate reasoning for top 100
    print(f"Generating reasoning for top {limit} candidates...")
    results = []
    for rank, item in enumerate(top_k, start=1):
        reasoning = generate_reasoning(item['candidate_data'], item['sub_scores'])
        results.append({
            'candidate_id': item['candidate_id'],
            'rank': rank,
            'score': round(item['score'], 4),
            'reasoning': reasoning
        })
        
    return results

def write_submission(results, out_path):
    print(f"Writing output to {out_path}...")
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['candidate_id', 'rank', 'score', 'reasoning'])
        writer.writeheader()
        writer.writerows(results)
    print("Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rank candidates for JD.")
    parser.add_argument('--candidates', type=str, required=True, help="Path to candidates.jsonl")
    parser.add_argument('--out', type=str, required=True, help="Path to output csv")
    
    args = parser.parse_args()
    
    results = process_candidates(args.candidates, limit=100)
    write_submission(results, args.out)
