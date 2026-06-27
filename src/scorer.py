import re
from datetime import datetime
from config import JD_RULES, WEIGHTS

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


def is_honeypot(candidate, global_stats=None):
    """
    Checks if a candidate is a honeypot based on impossible patterns.
    """
    for skill in candidate.get('skills', []):
        if skill.get('proficiency') == 'expert' and skill.get('duration_months', 1) == 0:
            return True
            
    stated_yoe = candidate.get('profile', {}).get('years_of_experience', 0)
    total_career_months = sum(job.get('duration_months', 0) for job in candidate.get('career_history', []))
    career_yoe = total_career_months / 12.0
    
    if stated_yoe > 5 and career_yoe < 1:
        return True
    if career_yoe > stated_yoe + 5:
        return True
        
    # Shannon Entropy Anomaly Checker
    if global_stats and 'entropy_mean' in global_stats:
        candidate_text = []
        for skill in candidate.get('skills', []):
            candidate_text.append(skill.get('name', '').lower())
        for job in candidate.get('career_history', []):
            candidate_text.append(job.get('title', '').lower())
            candidate_text.append(job.get('description', '').lower())
        full_text = ' '.join(candidate_text)
        
        ent = calculate_text_entropy(full_text)
        mean = global_stats['entropy_mean']
        std = global_stats['entropy_std']
        
        if std > 0.1:
            if abs(ent - mean) > 2.0 * std:
                return True
        else:
            if ent < 2.0 or ent > 8.0:
                return True
                
    return False

def score_skills_semantic(candidate, custom_weights=None, global_stats=None):
    """
    Replaces keyword matching with Semantic Cluster mapping.
    Evaluates how many functional clusters the candidate satisfies.
    """
    weights = custom_weights if custom_weights else WEIGHTS
    clusters = JD_RULES.get('semantic_clusters', {})
    if not clusters:
        return 0
        
    candidate_text = []
    for skill in candidate.get('skills', []):
        candidate_text.append(skill.get('name', '').lower())
    for job in candidate.get('career_history', []):
        candidate_text.append(job.get('title', '').lower())
        candidate_text.append(job.get('description', '').lower())
        
    full_text = ' '.join(candidate_text)
    
    matched_clusters = []
    cluster_scores = {}
    
    import math
    total_candidates = global_stats.get('total_candidates', 0) if global_stats else 0
    keyword_counts = global_stats.get('keyword_counts', {}) if global_stats else {}
    
    def get_idf(kw):
        if total_candidates > 0 and kw in keyword_counts:
            count = keyword_counts[kw]
            return math.log(1.0 + (total_candidates / (1.0 + count)))
        return 1.0

    for cluster_name, keywords in clusters.items():
        cluster_idfs = []
        matched_idfs = []
        for kw in keywords:
            kw_lower = kw.lower()
            idf = get_idf(kw_lower)
            cluster_idfs.append(idf)
            if kw_lower in full_text:
                matched_idfs.append(idf)
                
        if cluster_idfs:
            mean_idf = sum(cluster_idfs) / len(cluster_idfs)
            if mean_idf > 0:
                c_score = min(1.0, sum(matched_idfs) / mean_idf)
            else:
                c_score = 1.0 if matched_idfs else 0.0
        else:
            c_score = 0.0
            
        if c_score > 0:
            matched_clusters.append(cluster_name)
            cluster_scores[cluster_name] = c_score
        else:
            cluster_scores[cluster_name] = 0.0

    total_clusters = len(clusters)
    if total_clusters == 0:
        return 0
        
    coverage = sum(cluster_scores.values()) / total_clusters
    
    # We want 80% coverage to equal 100 points
    raw_score = min(100, (coverage / 0.8) * 100)
    
    # Co-occurrence Skill Cohesion (Jaccard-based logic)
    has_advanced = any(c in matched_clusters for c in ["Vector_Databases", "Retrieval_Ranking", "LLM_Engineering", "Infrastructure"])
    has_foundation = "Core_Programming" in matched_clusters
    
    cohesion_factor = 1.0
    if has_advanced and not has_foundation:
        cohesion_factor = 0.8 # 20% discount if advanced skills are listed without Core Programming
        
    final_skills_score = (raw_score / 100.0) * weights['skills'] * cohesion_factor
    return final_skills_score, matched_clusters

def score_career_trajectory(candidate, custom_weights=None, global_stats=None):
    """
    Analyzes promotion velocity and company pedigree via PageRank.
    """
    weights = custom_weights if custom_weights else WEIGHTS
    profile = candidate.get('profile', {})
    yoe = profile.get('years_of_experience', 0)
    
    raw_score = 0
    ideal_min = JD_RULES['experience']['ideal_min']
    ideal_max = JD_RULES['experience']['ideal_max']
    abs_min = JD_RULES['experience']['absolute_min']
    
    if ideal_min <= yoe <= ideal_max:
        yoe_score = 50
    elif yoe >= abs_min and yoe < ideal_min:
        yoe_score = 25 + 25 * ((yoe - abs_min) / (ideal_min - abs_min) if ideal_min != abs_min else 1)
    elif yoe > ideal_max:
        decay = (yoe - ideal_max) * 2.5
        yoe_score = max(20, 50 - decay) 
    else:
        yoe_score = 5
        
    trajectory_score = 25
    career = candidate.get('career_history', [])
    
    tiers = JD_RULES.get('company_tiers', {})
    tier_1 = [c.lower() for c in tiers.get('tier_1', [])]
    consulting = [c.lower() for c in tiers.get('consulting', [])]
    
    has_tier_1 = False
    all_consulting = True if career else False
    
    seniority_levels = {'junior': 1, 'associate': 1, 'mid': 2, 'senior': 3, 'lead': 4, 'principal': 5, 'staff': 5}
    highest_level = 0
    
    levels = []
    durations = []
    
    for job in career:
        company = job.get('company', '').lower()
        title = job.get('title', '').lower()
        
        if any(t1 in company for t1 in tier_1):
            has_tier_1 = True
            all_consulting = False
        elif not any(cons in company for cons in consulting):
            all_consulting = False
            
        lvl = 2 
        for kw, level in seniority_levels.items():
            if kw in title:
                lvl = level
                if level > highest_level:
                    highest_level = level
                break
        
        levels.append(lvl)
        durations.append(job.get('duration_months', 0))
        
    if has_tier_1:
        trajectory_score += 15
    if all_consulting:
        trajectory_score -= 15 
        
    # Company PageRank Pedigree Boost
    pagerank_map = global_stats.get('company_pageranks', {}) if global_stats else {}
    highest_pr = 0.0
    for job in career:
        company = job.get('company', '').strip().lower()
        pr = pagerank_map.get(company, 0.0)
        if pr > highest_pr:
            highest_pr = pr
            
    if highest_pr >= 0.5:
        trajectory_score += int(highest_pr * 10)
        
    if highest_level >= 3 and yoe <= 5 and yoe > 0:
        trajectory_score += 10
        
    if len(levels) >= 2:
        lvl_start = levels[-1]
        lvl_end = levels[0]
        total_months = sum(durations)
        total_years = total_months / 12.0
        
        if total_years > 0:
            velocity_gradient = (lvl_end - lvl_start) / total_years
        else:
            velocity_gradient = 0.0
            
        if velocity_gradient >= 0.4 and lvl_end > lvl_start:
            trajectory_score += 10
            
    trajectory_score = max(0, min(50, trajectory_score))
    raw_score = yoe_score + trajectory_score
    
    velocity_metrics = {
        'highest_level': highest_level,
        'has_tier_1': has_tier_1,
        'all_consulting': all_consulting
    }
            
    return (raw_score / 100.0) * weights['experience'], velocity_metrics

def score_behavioral_intent(candidate, custom_weights=None, global_stats=None):
    weights = custom_weights if custom_weights else WEIGHTS
    signals = candidate.get('redrob_signals', {})
    if not signals:
        return 0, "No data"
        
    raw_score = 50
    rr = signals.get('recruiter_response_rate', 0.5)
    raw_score += (rr - 0.5) * 40 
    
    if signals.get('open_to_work_flag'):
        raw_score += 15
        
    comp = signals.get('profile_completeness_score', 50)
    raw_score += (comp - 50) * 0.2
    
    gh = signals.get('github_activity_score', -1)
    if gh > 50:
        raw_score += 10
        
    last_active = signals.get('last_active_date')
    status = "Active"
    
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            parts = [int(p) for p in date_str.split('-')[:3]]
            if len(parts) == 3:
                import datetime
                return datetime.date(parts[0], parts[1], parts[2])
        except:
            pass
        return None

    if last_active:
        decay_mult = 1.0
        if global_stats and global_stats.get('latest_active_date'):
            ref_date = parse_date(global_stats['latest_active_date'])
            cand_date = parse_date(last_active)
            if ref_date and cand_date:
                delta_days = (ref_date - cand_date).days
                if delta_days > 0:
                    import math
                    decay_mult = math.exp(-0.00385 * delta_days)
        else:
            if '2023' in last_active or '2022' in last_active:
                decay_mult = 0.25
                
        penalty = 30.0 * (1.0 - decay_mult)
        raw_score -= penalty
        status = "Active" if decay_mult > 0.8 else ("Moderate" if decay_mult > 0.5 else "Stale")
            
    raw_score = max(0, min(100, raw_score))
    return (raw_score / 100.0) * weights['behavioral'], status

def score_location(candidate, custom_weights=None, global_stats=None):
    weights = custom_weights if custom_weights else WEIGHTS
    profile = candidate.get('profile', {})
    loc = profile.get('location', '').lower()
    
    raw_score = 0
    
    for pref in JD_RULES['locations']['preferred']:
        if pref.lower() in loc:
            raw_score = 100
            break
            
    if raw_score == 0:
        for acc in JD_RULES['locations']['acceptable']:
            if acc.lower() in loc:
                raw_score = 70
                break
                
    if raw_score == 0:
        signals = candidate.get('redrob_signals', {})
        if signals.get('willing_to_relocate'):
            raw_score = 60
        else:
            raw_score = 20
            
    return (raw_score / 100.0) * weights['location']

def score_candidate(candidate, custom_weights=None, global_stats=None):
    """
    Returns (total_score, sub_scores, is_honeypot_flag)
    """
    if is_honeypot(candidate, global_stats=global_stats):
        return 0, {}, True
        
    s_skills, matched_clusters = score_skills_semantic(candidate, custom_weights=custom_weights, global_stats=global_stats)
    s_exp, velocity = score_career_trajectory(candidate, custom_weights=custom_weights, global_stats=global_stats)
    s_beh, beh_status = score_behavioral_intent(candidate, custom_weights=custom_weights, global_stats=global_stats)
    s_loc = score_location(candidate, custom_weights=custom_weights, global_stats=global_stats)
    
    total = s_skills + s_exp + s_beh + s_loc
    total_normalized = total / 100.0
    
    sub_scores = {
        'skills': s_skills,
        'experience': s_exp,
        'behavioral': s_beh,
        'location': s_loc,
        'matched_clusters': matched_clusters,
        'velocity': velocity,
        'beh_status': beh_status
    }
    
    return total_normalized, sub_scores, False
