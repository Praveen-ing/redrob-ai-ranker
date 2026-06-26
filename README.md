# Redrob AI Ranker

This repository contains our team's submission for the Intelligent Candidate Discovery & Ranking Challenge.

## Approach
Our ranker strictly complies with the hackathon's rules by running purely offline locally within the 5-minute CPU constraint, utilizing zero hosted LLM API calls during the ranking step.

The system relies on a high-speed Python heuristic scoring engine that incorporates:
- Exact and partial keyword matches of AI skills mapped directly from the JD.
- Penalties for profiles consisting exclusively of consulting experience.
- Experience mapping onto the 5-9 year ideal band.
- Behavioral signal boosts for candidates who are open-to-work, have high recruiter response rates, and recent activity.
- Automatic honeypot filtering based on anomalous profile activity (e.g. "expert" proficiency with 0 months used).
- A dynamic reasoning string builder.

## Requirements
The engine was built using purely the Python Standard Library.
No external dependencies are required. Just run it with standard Python 3.

## Reproduction
To reproduce our `team_submission.csv`, run:

```bash
python run.py --candidates ./path/to/candidates.jsonl --out team_submission.csv
```
