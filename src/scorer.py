import re
from datetime import datetime
from config import JD_RULES, WEIGHTS

def is_honeypot(candidate):
    """
    Checks if a candidate is a honeypot.
    Known honeypot patterns from docs:
    - 'expert' proficiency with 0 duration_months
    - Mismatched career history years vs stated years_of_experience (extreme mismatch)
    """
    # 1. Expert with 0 months
    for skill in candidate.get('skills', []):
        if skill.get('proficiency') == 'expert' and skill.get('duration_months', 1) == 0:
            return True
            
    # 2. Total duration mismatch
    stated_yoe = candidate.get('profile', {}).get('years_of_experience', 0)
    total_career_months = sum(job.get('duration_months', 0) for job in candidate.get('career_history', []))
    career_yoe = total_career_months / 12.0
    
    # If stated YOE is very large (e.g., 10) but career history has < 1 year
    if stated_yoe > 5 and career_yoe < 1:
        return True
    
    # If career history is way larger than stated YOE
    if career_yoe > stated_yoe + 5:
        return True

    return False

def score_skills(candidate):
    """
    Scores skills out of 100, then weighted to WEIGHTS['skills'].
    Looks at explicit skills array and career history descriptions.
    """
    score = 0
    max_score = 100
    
    core_skills = [s.lower() for s in JD_RULES['core_skills']]
    bonus_skills = [s.lower() for s in JD_RULES['bonus_skills']]
    
    candidate_text = []
    
    # Add skills
    for skill in candidate.get('skills', []):
        name = skill.get('name', '').lower()
        candidate_text.append(name)
        # Bonus for high proficiency in matched skills is implicit by just matching, 
        # but we could weight proficiency
        
    # Add career history text
    for job in candidate.get('career_history', []):
        candidate_text.append(job.get('title', '').lower())
        candidate_text.append(job.get('description', '').lower())
        
    full_text = ' '.join(candidate_text)
    
    # Count core skill matches
    matched_core = 0
    for cs in core_skills:
        # basic word boundary matching for some, substring for others
        if cs in full_text:
            matched_core += 1
            
    # Count bonus skill matches
    matched_bonus = 0
    for bs in bonus_skills:
        if bs in full_text:
            matched_bonus += 1
            
    # Calculate score
    # Let's say matching 6 core skills gives 80 points, bonus skills give extra
    core_score = min(80, (matched_core / 6) * 80)
    bonus_score = min(20, matched_bonus * 5)
    
    raw_score = core_score + bonus_score
    
    return (raw_score / 100.0) * WEIGHTS['skills']

def score_experience(candidate):
    """
    Scores experience out of 100, then weighted.
    Penalizes purely consulting background.
    """
    profile = candidate.get('profile', {})
    yoe = profile.get('years_of_experience', 0)
    
    raw_score = 0
    ideal_min = JD_RULES['experience']['ideal_min']
    ideal_max = JD_RULES['experience']['ideal_max']
    abs_min = JD_RULES['experience']['absolute_min']
    
    if ideal_min <= yoe <= ideal_max:
        raw_score = 100
    elif yoe >= abs_min and yoe < ideal_min:
        # linear scale from abs_min (e.g. 4) -> 50 points to ideal_min (5) -> 100 points
        raw_score = 50 + 50 * ((yoe - abs_min) / (ideal_min - abs_min) if ideal_min != abs_min else 1)
    elif yoe > ideal_max:
        # drops off slowly after ideal_max
        decay = (yoe - ideal_max) * 5
        raw_score = max(40, 100 - decay) 
    else:
        raw_score = 10  # too junior
        
    # Check for pure consulting
    career = candidate.get('career_history', [])
    if career:
        consulting_firms = [f.lower() for f in JD_RULES['disqualifiers']['consulting_only']]
        all_consulting = True
        for job in career:
            company = job.get('company', '').lower()
            is_consulting = False
            for cf in consulting_firms:
                if cf in company:
                    is_consulting = True
                    break
            if not is_consulting:
                all_consulting = False
                break
                
        if all_consulting:
            raw_score *= 0.3 # Heavy penalty for pure consulting
            
    return (raw_score / 100.0) * WEIGHTS['experience']

def score_behavioral(candidate):
    """
    Scores behavioral signals out of 100, then weighted.
    """
    signals = candidate.get('redrob_signals', {})
    if not signals:
        return 0
        
    raw_score = 50 # Base score
    
    # Response rate (0 to 1)
    rr = signals.get('recruiter_response_rate', 0.5)
    raw_score += (rr - 0.5) * 40 # +/- 20 points
    
    # Recency (last_active_date)
    last_active = signals.get('last_active_date')
    if last_active:
        try:
            # Assuming format is YYYY-MM-DD and dataset is circa 2026? 
            # Or we can just parse and sort. Let's assume current date is 2024-01-01 for scoring, 
            # or better, we can just look at if they are open to work
            pass
        except:
            pass
            
    if signals.get('open_to_work_flag'):
        raw_score += 10
        
    # Profile completeness
    comp = signals.get('profile_completeness_score', 50)
    raw_score += (comp - 50) * 0.2
    
    # Github activity
    gh = signals.get('github_activity_score', -1)
    if gh > 0:
        raw_score += (gh / 100.0) * 10
        
    raw_score = max(0, min(100, raw_score))
    return (raw_score / 100.0) * WEIGHTS['behavioral']

def score_location(candidate):
    """
    Scores location out of 100, then weighted.
    """
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
        # Check willingness to relocate
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
        
    s_skills = score_skills(candidate)
    s_exp = score_experience(candidate)
    s_beh = score_behavioral(candidate)
    s_loc = score_location(candidate)
    
    total = s_skills + s_exp + s_beh + s_loc
    # Normalize to 0-1 range
    total_normalized = total / 100.0
    
    sub_scores = {
        'skills': s_skills,
        'experience': s_exp,
        'behavioral': s_beh,
        'location': s_loc
    }
    
    return total_normalized, sub_scores, False
