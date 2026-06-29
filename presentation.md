---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #0f172a
color: #f8fafc
style: |
  section {
    font-family: 'Inter', sans-serif;
    padding: 60px;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  }
  h1 {
    color: #38bdf8;
    font-size: 2.8rem;
    font-weight: 800;
  }
  h2 {
    color: #38bdf8;
    font-size: 2.2rem;
    font-weight: 700;
    border-bottom: 2px solid rgba(129, 140, 248, 0.3);
    padding-bottom: 10px;
  }
  h3 {
    color: #818cf8;
  }
  footer {
    color: #94a3b8;
    font-size: 0.8rem;
  }
  strong {
    color: #f43f5e;
  }
  li {
    font-size: 1.1rem;
    margin-bottom: 8px;
  }
  p {
    font-size: 1.2rem;
  }
---

# 🟥 Redrob Data & AI Challenge
## Rethinking Candidate Discovery

Beyond Keywords. Understanding Meaning, Trajectory, and Intent.

**Team Submission** | India Runs Challenge

---

## 🎯 The Problem with Modern Recruiting

### Keyword Matching is Broken

* **The Symptom:** Recruiters receive thousands of applications. ATS systems rank them by counting keywords.
* **The Result:** 
  * *"Keyword stuffers"* (candidates who paste the JD into their resume) rank at the top.
  * True experts (who describe their actual complex work) get buried.
* **The Goal:** Build a system that ranks candidates the way an expert human recruiter would.

---

## 🧠 Our Approach: 4 Pillars of Ranking

Our engine doesn't just read words; it scores on four weighted axes:

1. **Semantic Competency (40%):** Does their experience map to the core skill clusters? (e.g. "Weaviate" $\rightarrow$ "Vector DB").
2. **Career Trajectory (30%):** Do they have promotion velocity? Tier-1 company experience?
3. **Behavioral Intent (20%):** Active seeker? High recruiter response rate?
4. **Location Fit (10%):** Does their geography align with business needs?

---

## 🛡️ Anti-Gaming & Honeypot Detection

### Defeating the "Keyword Stuffers"

We implemented robust anomaly detection to filter out fake or inflated profiles:

* **The "Instant Expert" Filter:** Flags profiles claiming "expert" proficiency in skills they've used for 0 months.
* **Experience Inconsistency:** Flags candidates claiming 10 years of experience but showing <1 year in their actual career history.
* **Shannon Entropy Analysis:** Statistically analyzes profile text. Devs with entropy $> 2\sigma$ from the mean are flagged.

---

## ⚡ The Architecture: Fast & Offline

### Lightning Fast. Fully Offline.

* **Backend Engine:** Pure Python. No heavy external dependencies.
* **Performance:** Processes 100,000+ candidate profiles in **under 35 seconds**.
* **Zero APIs:** Zero external LLM API calls during the ranking step to guarantee execution within the 5-minute offline CPU limit.
* **Explainable AI (XAI):** Generates deterministic, human-readable rationale for *why* a candidate was ranked highly.

---

## 🖥️ The Judge's Dashboard (UI)

### Beautiful, Interactive, and Transparent

* **Zero Setup:** A pure HTML/JS application with zero build steps.
* **Key Features:** 
  * Configure the target role requirements dynamically.
  * Upload the ranked CSV.
  * View deep scoring breakdowns with progress bars.
  * Search, sort, and export candidate data visually.

---

## 🏆 Conclusion & Impact

### Hiring, Solved.

* **For Recruiters:** Reduces time-to-shortlist from days to **35 seconds**.
* **For Candidates:** Rewards actual career growth and skill clusters, not just resume hacking.
* **For Redrob:** A production-ready, highly scalable heuristic engine that can be adapted to any job description via a simple JSON config.

**Thank you! Check out our GitHub Repo.**
