import re
from datetime import datetime
from config import JD_RULES, WEIGHTS

def is_honeypot(candidate):
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
    return False

def score_skills_semantic(candidate):
    """
    Replaces keyword matching with Semantic Cluster mapping.
    Evaluates how many functional clusters the candidate satisfies.
    """
    clusters = JD_RULES.get('semantic_clusters', {})
    if not clusters:
        # Fallback to old behavior if dict not updated
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
    
    for cluster_name, keywords in clusters.items():
        # Check if ANY keyword in the cluster exists in the candidate's profile
        cluster_hit = False
        for kw in keywords:
            if kw in full_text:
                cluster_hit = True
                break
        
        if cluster_hit:
            matched_clusters.append(cluster_name)
            cluster_scores[cluster_name] = 1.0
        else:
            cluster_scores[cluster_name] = 0.0

    # Calculate base score based on cluster coverage
    total_clusters = len(clusters)
    if total_clusters == 0:
        return 0
        
    coverage = len(matched_clusters) / total_clusters
    
    # We want 80% coverage to equal 100 points
    raw_score = min(100, (coverage / 0.8) * 100)
    
    return (raw_score / 100.0) * WEIGHTS['skills'], matched_clusters

def score_career_trajectory(candidate):
    """
    Analyzes promotion velocity and company tiering.
    """
    profile = candidate.get('profile', {})
    yoe = profile.get('years_of_experience', 0)
    
    raw_score = 0
    ideal_min = JD_RULES['experience']['ideal_min']
    ideal_max = JD_RULES['experience']['ideal_max']
    abs_min = JD_RULES['experience']['absolute_min']
    
    # 1. Base YOE Score (0 - 50 points)
    if ideal_min <= yoe <= ideal_max:
        yoe_score = 50
    elif yoe >= abs_min and yoe < ideal_min:
        yoe_score = 25 + 25 * ((yoe - abs_min) / (ideal_min - abs_min) if ideal_min != abs_min else 1)
    elif yoe > ideal_max:
        decay = (yoe - ideal_max) * 2.5
        yoe_score = max(20, 50 - decay) 
    else:
        yoe_score = 5
        
    # 2. Promotion Velocity & Tiering (0 - 50 points)
    trajectory_score = 25
    career = candidate.get('career_history', [])
    
    tiers = JD_RULES.get('company_tiers', {})
    tier_1 = [c.lower() for c in tiers.get('tier_1', [])]
    consulting = [c.lower() for c in tiers.get('consulting', [])]
    
    has_tier_1 = False
    all_consulting = True if career else False
    
    seniority_levels = {'junior': 1, 'associate': 1, 'mid': 2, 'senior': 3, 'lead': 4, 'principal': 5, 'staff': 5}
    highest_level = 0
    
    for job in career:
        company = job.get('company', '').lower()
        title = job.get('title', '').lower()
        
        # Tiering check
        if any(t1 in company for t1 in tier_1):
            has_tier_1 = True
            all_consulting = False
        elif not any(cons in company for cons in consulting):
            all_consulting = False
            
        # Seniority extraction
        for kw, level in seniority_levels.items():
            if kw in title and level > highest_level:
                highest_level = level
                
    if has_tier_1:
        trajectory_score += 15
    if all_consulting:
        trajectory_score -= 15 # Penalize pure consulting
        
    # Velocity: If they reached Senior+ in < 5 years, boost
    if highest_level >= 3 and yoe <= 5 and yoe > 0:
        trajectory_score += 10
        
    trajectory_score = max(0, min(50, trajectory_score))
    raw_score = yoe_score + trajectory_score
    
    velocity_metrics = {
        'highest_level': highest_level,
        'has_tier_1': has_tier_1,
        'all_consulting': all_consulting
    }
            
    return (raw_score / 100.0) * WEIGHTS['experience'], velocity_metrics

def score_behavioral_intent(candidate):
    """
    Calculates Engagement/Intent Score based on platform activity.
    Downweights inactive candidates heavily.
    """
    signals = candidate.get('redrob_signals', {})
    if not signals:
        return 0, "No data"
        
    raw_score = 50
    
    # Recruiter Response Rate
    rr = signals.get('recruiter_response_rate', 0.5)
    raw_score += (rr - 0.5) * 40 
    
    # Open to work flag is a massive signal
    if signals.get('open_to_work_flag'):
        raw_score += 15
        
    # Profile Completeness
    comp = signals.get('profile_completeness_score', 50)
    raw_score += (comp - 50) * 0.2
    
    # Github activity bonus
    gh = signals.get('github_activity_score', -1)
    if gh > 50:
        raw_score += 10
        
    # INACTIVITY PENALTY: (Simulated)
    # The JD explicitly mentions down-weighting inactive candidates.
    last_active = signals.get('last_active_date')
    status = "Active"
    if last_active:
        # In a real system, we'd compare to current date.
        # For the hackathon dataset, we look at the year. If it's old, penalize.
        if '2023' in last_active or '2022' in last_active:
            raw_score -= 30
            status = "Stale"
            
    raw_score = max(0, min(100, raw_score))
    return (raw_score / 100.0) * WEIGHTS['behavioral'], status

def score_location(candidate):
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
            
    return (raw_score / 100.0) * WEIGHTS['location']

def score_candidate(candidate):
    """
    Returns (total_score, sub_scores, is_honeypot_flag)
    """
    if is_honeypot(candidate):
        return 0, {}, True
        
    s_skills, matched_clusters = score_skills_semantic(candidate)
    s_exp, velocity = score_career_trajectory(candidate)
    s_beh, beh_status = score_behavioral_intent(candidate)
    s_loc = score_location(candidate)
    
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
