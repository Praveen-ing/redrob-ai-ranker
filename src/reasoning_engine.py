from config import JD_RULES

def generate_reasoning(candidate, sub_scores):
    """
    Generates a plain-language reasoning string for the top candidates.
    This replaces the need for a hosted LLM, keeping the generation deterministic,
    fact-based, and fast.
    """
    profile = candidate.get('profile', {})
    yoe = profile.get('years_of_experience', 0)
    title = profile.get('current_title', 'Engineer')
    
    # Extract matched skills
    core_skills = [s.lower() for s in JD_RULES['core_skills']]
    
    candidate_text_list = []
    for skill in candidate.get('skills', []):
        candidate_text_list.append(skill.get('name', '').lower())
    for job in candidate.get('career_history', []):
        candidate_text_list.append(job.get('title', '').lower())
        candidate_text_list.append(job.get('description', '').lower())
        
    full_text = ' '.join(candidate_text_list)
    
    matched = []
    for cs in core_skills:
        if cs in full_text:
            matched.append(cs)
            
    # Capitalize matched skills nicely for the sentence
    matched_nice = [m.title() if m.islower() else m for m in matched]
    
    # Select top 3 matched skills
    top_skills = matched_nice[:3]
    skills_str = ", ".join(top_skills) if top_skills else "relevant AI technologies"
    
    # Behavioral insights
    signals = candidate.get('redrob_signals', {})
    rr = signals.get('recruiter_response_rate', 0.5)
    rr_str = f"high ({rr:.2f})" if rr >= 0.7 else (f"moderate ({rr:.2f})" if rr >= 0.4 else f"low ({rr:.2f})")
    
    # Location
    loc = profile.get('location', 'Unknown')
    
    # Build sentence
    reasoning_parts = []
    
    # Experience and role
    reasoning_parts.append(f"{title} with {yoe} years of experience.")
    
    # Skills
    if len(top_skills) > 1:
        reasoning_parts.append(f"Strong match for core stack including {skills_str}.")
    elif len(top_skills) == 1:
        reasoning_parts.append(f"Experience includes {skills_str}.")
        
    # Behavioral & Location
    if signals.get('open_to_work_flag'):
        reasoning_parts.append(f"Currently open to work with a {rr_str} response rate.")
    else:
        reasoning_parts.append(f"Recruiter response rate is {rr_str}.")
        
    # Consulting check (if they got penalized but still made it)
    if sub_scores.get('experience', 0) < 10 and yoe > 4:
        reasoning_parts.append("Background is heavily consulting-focused, but skill overlap is significant.")
        
    reasoning = " ".join(reasoning_parts)
    return reasoning
