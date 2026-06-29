# Redrob AI Ranker

> **India Runs — Data & AI Challenge** | Intelligent Candidate Discovery & Ranking


A **production-grade, fully offline AI candidate ranking engine** built for the Redrob Data & AI Hackathon. It processes **100,000+ candidate profiles in under 35 seconds** — with zero API calls, zero internet dependency, and a transparent scoring system that works like an expert recruiter, not a keyword matcher.

---


## The Problem We're Solving

Traditional HR tools rank candidates by **keyword frequency**. If a job description says "Python", the tool finds everyone who wrote "Python" anywhere on their resume. This limits the scope of evaluation.

This approach is often inadequate. A junior developer who pastes keywords scores higher than a senior engineer who describes their actual work. The result? Recruiters waste hours manually sifting through mismatched profiles.

**Our system thinks differently.** Instead of counting keywords, it understands *meaning*, *trajectory*, and *intent* — the way a great human recruiter would.

---

## Key Features

### Semantic Skill Matching (not keyword matching)
Skills are grouped into **5 semantic clusters** (defined in `data/jd_rules.json`):

| Cluster | Covers |
|---|---|
| **Core Programming** | Python, Go, C++, Java |
| **Vector Databases** | Pinecone, Weaviate, Qdrant, Milvus, FAISS, ChromaDB |
| **Retrieval & Ranking** | BM25, Cross-encoders, Sentence-Transformers, NDCG, Hybrid Search |
| **LLM Engineering** | Fine-tuning, LoRA, QLoRA, LangChain, HuggingFace, Prompt Engineering |
| **Infrastructure** | Docker, Kubernetes, FastAPI, AWS, GCP, ONNX, TensorRT |

A candidate doesn't need to match the *exact* keyword. They get credit for the *entire semantic cluster* they demonstrate competency in.

### Career Trajectory Analysis
The engine doesn't just count years — it analyses the *shape* of a career:
- **Promotion Velocity**: Were they promoted quickly? Multiple senior titles = high signal
- **Company Tiering**: Tier-1 companies (Google, Microsoft, OpenAI, Anthropic, etc.) get a score boost
- **Consulting Penalty**: Pure consulting profiles (TCS, Infosys, Wipro, etc.) are down-weighted when the role requires product-building instincts
- **Experience Band Fit**: Ideal 5–9 years gets full marks; under/over gets a graded penalty

### Behavioral Intent Scoring
The system reads engagement signals that indicate whether a candidate is *actually* looking:
- **Recruiter Response Rate**: Candidates who historically respond quickly rank higher
- **Open-to-Work Status**: Active job seekers get a meaningful boost
- **Platform Activity**: Recently active candidates signal genuine interest
- **Notice Period**: Shorter notice periods preferred; very long ones penalised

### Location Intelligence
- **Preferred cities** (Pune, Noida, Delhi NCR): Full score
- **Acceptable cities** (Bangalore, Hyderabad, Mumbai, Chennai): Moderate score
- **Remote / other**: Neutral score

### Honeypot Detection (Anti-Gaming)
The system automatically identifies and filters out fake or inflated profiles using:
1. **Impossible Skill Claims**: Expert proficiency + 0 months used = instant disqualification
2. **Experience Inconsistency**: Stated 10 years experience but career history shows <1 year
3. **Shannon Entropy Anomaly Detection**: Profiles whose text entropy deviates by more than 2 standard deviations from the population mean are flagged as statistically anomalous

### Explainable AI (XAI) Reasoning
Every shortlisted candidate comes with a **deterministic, data-driven rationale** — not a generic template. The reasoning engine generates context-aware justifications based on the candidate's actual scores, cluster matches, and behavioral signals.

---

## Architecture

```
redrob-ai-ranker/
│
├── run.py                     # Main orchestrator — reads JSONL, runs pipeline, outputs CSV
│
├── src/
│   ├── scorer.py              # Core ranking engine (semantic scoring, trajectory, behavior)
│   ├── reasoning_engine.py    # XAI — generates human-readable candidate rationale
│   └── config.py              # Loads jd_rules.json, defines scoring weights
│
├── data/
│   └── jd_rules.json          # Job Description config (role, skills, locations, tiers)
│
├── frontend/
│   └── index.html             # Interactive UI dashboard (pure HTML/JS, zero dependencies)
│
├── team_submission.csv        # Final ranked output for hackathon submission
├── requirements.txt           # Python dependencies (standard lib only for core engine)
└── submission_metadata.yaml   # Hackathon submission metadata
```

---

## How the Scoring Works

Each candidate receives a **final composite score between 0.0 and 1.0**, calculated as a weighted sum of 4 axes:

```
Final Score = (Skills × 0.40) + (Experience × 0.30) + (Behavior × 0.20) + (Location × 0.10)
```

### Scoring Breakdown

**Skills (40% weight)**
```python
score = matched_clusters / total_clusters
# Bonus: +0.1 for each Tier-1 company in career history
# Penalty: -0.15 if profile is pure consulting with no product exp
```

**Career Trajectory (30% weight)**
```python
# Experience band fit
if ideal_min <= years <= ideal_max:    base = 1.0
elif years >= absolute_min:            base = 0.5 + linear_decay
else:                                  base = 0.2

# Promotion velocity bonus (up to +0.2)
senior_roles = count(titles containing "senior", "lead", "principal", "staff", "head")
velocity_bonus = min(senior_roles * 0.05, 0.2)
```

**Behavioral Intent (20% weight)**
```python
score = (response_rate × 0.5) + (open_to_work × 0.3) + (activity_recency × 0.2)
```

**Location (10% weight)**
```python
if city in preferred:   score = 1.0
if city in acceptable:  score = 0.7
else:                   score = 0.4
```

### Tie-Breaking
When two candidates share the same score (to 4 decimal places), they are sorted by `candidate_id` alphabetically — ensuring **fully deterministic, reproducible** results across every run.

---

## Why This Is Reliable

### Fully Offline — No API Calls
The entire pipeline runs on your local machine with Python's standard library. There are **zero calls to OpenAI, Claude, Gemini, or any external service**. This means:
- Works in the hackathon sandbox environment (no internet access)
- Finishes within the 5-minute CPU time limit
- No rate limits, no latency, no cost

### Deterministic & Reproducible
Run it 100 times on the same input — you get the exact same output. There are no random seeds, no model stochasticity, no probabilistic decisions. The same candidate always gets the same score.

### Transparent & Explainable
Every score is broken down into sub-components. You can look at any candidate and understand precisely why they ranked where they did. There is no black-box inference happening.

### Anti-Gaming
The Shannon entropy check + experience inconsistency check ensures that candidates who try to pad their profiles with keywords are either penalised or filtered. Real experience scores higher than copied buzzwords.

### Configurable for Any Role
The entire job description is defined in one human-readable JSON file. No code changes required to hire for a completely different role — just update `data/jd_rules.json`.

---

## Interactive Dashboard UI

The project includes a premium interactive web dashboard at `frontend/index.html`. It is a **pure HTML + JavaScript single file** — no build step, no npm, no framework required. Just open it in any browser.

### UI Features
| Feature | Description |
|---|---|
| **Role Setup (Step 1)** | Define the target role before viewing results — quick presets or fully custom |
| **Skill Tag Input** | Type a skill and press Enter to add it as a chip; click suggestions |
| **Location Picker** | Tag-based city input with common suggestions pre-loaded |
| **Role Summary Card** | On the upload screen, see a recap of what you configured |
| **CSV Upload** | Drag-and-drop or browse for your `team_submission.csv` |
| **Processing Animation** | Live progress bar with phase-by-phase status updates |
| **Candidate Cards** | Each card shows rank, score, AI rationale + 4 mini score bars |
| **Click-to-Expand Modal** | Full scoring breakdown with individual bar charts per axis |
| **Search & Filter** | Real-time search by candidate ID or reasoning text |
| **Score Distribution** | Sidebar histogram showing how scores spread across the shortlist |
| **Export CSV** | One-click re-export of the filtered/sorted results |

### UI Screenshots Flow
```
Step 1: Define Role → Step 2: Upload CSV → Step 3: Processing → Step 4: Results Dashboard
```

---

## How to Run

### Prerequisites
- Python 3.8 or higher
- Any modern web browser (for the UI)

### Step 1 — Generate the Ranked CSV (CLI)
```bash
# Clone the repo
git clone https://github.com/Praveen-ing/redrob-ai-ranker.git
cd redrob-ai-ranker

# Run the ranking engine
python run.py \
  --candidates "./path/to/candidates.jsonl" \
  --out team_submission.csv

# Optional: limit to top N candidates
python run.py --candidates ./candidates.jsonl --out team_submission.csv --limit 100
```

This outputs a `team_submission.csv` file with columns: `rank`, `candidate_id`, `score`, `reasoning`.

### Step 2 — View the Dashboard (UI)
```bash
# Serve the frontend (any static server works)
cd frontend
python -m http.server 3000

# Then open: http://localhost:3000
```

Or simply double-click `frontend/index.html` to open it directly in your browser.

---

## Customising for a Different Role

All role configuration lives in one file: [`data/jd_rules.json`](data/jd_rules.json)

```json
{
  "target_role": "Senior AI Engineer",
  "experience": {
    "ideal_min": 5,
    "ideal_max": 9,
    "absolute_min": 4
  },
  "semantic_clusters": {
    "Core_Programming": ["python", "golang", "c++"],
    "LLM_Engineering":  ["llm", "fine-tuning", "langchain", "huggingface"],
    "Vector_Databases": ["pinecone", "faiss", "weaviate", "chromadb"]
  },
  "locations": {
    "preferred":   ["Pune", "Noida", "Delhi NCR"],
    "acceptable":  ["Bangalore", "Hyderabad", "Mumbai"]
  },
  "company_tiers": {
    "tier_1":    ["google", "microsoft", "amazon", "openai", "anthropic"],
    "consulting": ["tcs", "infosys", "wipro", "accenture"]
  }
}
```

Edit this file, save it, and re-run `python run.py`. That's it — no code changes needed.

---

## Performance

| Metric | Value |
|---|---|
| Dataset size | 100,000+ candidate profiles |
| Processing time | ~34 seconds on a standard CPU |
| Memory usage | < 500 MB RAM |
| API calls | **Zero** |
| External dependencies | **Zero** (pure Python stdlib for core engine) |
| Hackathon time limit | 5 minutes (we're 8× faster) |

---

## Output Format

The `team_submission.csv` output strictly follows the hackathon submission schema:

```csv
rank,candidate_id,score,reasoning
1,CAND_0004989,0.9512,"Exceptional technical fit across LLM Engineering, Vector Databases..."
2,CAND_0001195,0.9487,"Strong ML engineering background with 8.7 years of progressive..."
...
```

| Column | Type | Description |
|---|---|---|
| `rank` | integer | 1-indexed rank (no ties at same rank) |
| `candidate_id` | string | Exact ID from input JSONL |
| `score` | float (4 dp) | Composite score 0.0–1.0 |
| `reasoning` | string | AI-generated rationale for this candidate's rank |

---

## Team TOPGUN

- **Nethavath Praveen** (Team Lead) - praveeeening@gmail.com
- **Abhinaya Nunna** - abhinayaseven@gmail.com
- **Botsa Radesh** - radeshbotsa@gmail.com
- **Sai Sameer Killamsetti** - saisameerkillamsetty8@gmail.com
