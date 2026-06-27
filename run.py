import argparse
import json
import csv
import sys
import os

# Add src to python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from scorer import score_candidate
from reasoning_engine import generate_reasoning
from config import JD_RULES

def calculate_text_entropy(text):
    import math
    import re
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    total_words = len(words)
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / total_words
        entropy -= p * math.log2(p)
    return entropy

def get_global_stats(candidates):
    all_keywords = []
    for cluster_name, kws in JD_RULES.get('semantic_clusters', {}).items():
        all_keywords.extend([k.lower() for k in kws])
    
    # Keep keywords unique
    all_keywords = list(set(all_keywords))
    keyword_counts = {kw: 0 for kw in all_keywords}
    
    latest_active_date = None
    entropies = []
    
    # PageRank Transition Graph data
    adj = {}
    all_companies_set = set()
    
    for candidate in candidates:
        candidate_text = []
        for skill in candidate.get('skills', []):
            candidate_text.append(skill.get('name', '').lower())
            
        career = candidate.get('career_history', [])
        comp_list = [job.get('company', '').strip() for job in career if job.get('company')]
        
        for job in career:
            candidate_text.append(job.get('title', '').lower())
            candidate_text.append(job.get('description', '').lower())
            
        full_text = ' '.join(candidate_text)
        entropies.append(calculate_text_entropy(full_text))
        
        for kw in all_keywords:
            if kw in full_text:
                keyword_counts[kw] += 1
                
        last_active = candidate.get('redrob_signals', {}).get('last_active_date')
        if last_active:
            if latest_active_date is None or last_active > latest_active_date:
                latest_active_date = last_active
                
        # Build directed graph of transitions
        if len(comp_list) >= 1:
            for c in comp_list:
                all_companies_set.add(c.lower())
        if len(comp_list) >= 2:
            chrono = comp_list[::-1] # chronological order (oldest to newest)
            for j in range(len(chrono) - 1):
                u = chrono[j].lower()
                v = chrono[j+1].lower()
                if u not in adj:
                    adj[u] = []
                adj[u].append(v)
                
    # Calculate PageRank
    companies = list(all_companies_set)
    N_comp = len(companies)
    company_pageranks = {}
    if N_comp > 0:
        pr = {c: 1.0 / N_comp for c in companies}
        d = 0.85
        for _ in range(10):
            new_pr = {c: (1.0 - d) / N_comp for c in companies}
            for u in companies:
                out_edges = adj.get(u, [])
                if out_edges:
                    for v in out_edges:
                        if v in new_pr:
                            new_pr[v] += d * (pr[u] / len(out_edges))
                else:
                    for v in companies:
                        new_pr[v] += d * (pr[u] / N_comp)
            pr = new_pr
            
        max_pr = max(pr.values()) if pr else 0.0
        if max_pr > 0:
            company_pageranks = {c: val / max_pr for c, val in pr.items()}
        else:
            company_pageranks = {c: 1.0 for c in pr.keys()}
            
    # Calculate Entropy Stats
    if entropies:
        import math
        mean_entropy = sum(entropies) / len(entropies)
        variance = sum((x - mean_entropy) ** 2 for x in entropies) / len(entropies)
        std_entropy = math.sqrt(variance)
    else:
        mean_entropy = 5.0
        std_entropy = 1.0
                
    return {
        'total_candidates': len(candidates),
        'keyword_counts': keyword_counts,
        'latest_active_date': latest_active_date,
        'entropy_mean': mean_entropy,
        'entropy_std': std_entropy,
        'company_pageranks': company_pageranks
    }


def process_candidates(candidates_path, limit=100, custom_weights=None):
    scored_candidates = []
    
    # Check if gzip or regular jsonl
    if candidates_path.endswith('.gz'):
        import gzip
        open_func = gzip.open
        mode = 'rt'
    else:
        open_func = open
        mode = 'r'
        
    print(f"Reading candidates from {candidates_path}...")
    
    candidates = []
    if candidates_path.endswith('.json'):
        with open_func(candidates_path, mode, encoding='utf-8') as f:
            candidates = json.load(f)
    else:
        with open_func(candidates_path, mode, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    candidates.append(json.loads(line))
                except Exception as e:
                    print(f"Error parsing candidate: {e}")
                    
    print(f"Pre-scanning {len(candidates)} candidates for global pool context...")
    global_stats = get_global_stats(candidates)
    
    print("Scoring candidates...")
    for i, candidate in enumerate(candidates):
        try:
            score, sub_scores, is_honeypot = score_candidate(candidate, custom_weights=custom_weights, global_stats=global_stats)
            if not is_honeypot:
                scored_candidates.append({
                    'candidate_id': candidate.get('candidate_id'),
                    'score': score,
                    'sub_scores': sub_scores,
                    'candidate_data': candidate
                })
        except Exception as e:
            print(f"Error processing candidate at index {i}: {e}")
                
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
