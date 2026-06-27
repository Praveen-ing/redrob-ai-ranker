# Redrob Data & AI Challenge — Presentation Deck Content

*Copy-paste this content into a presentation tool like Canva, Google Slides, or PowerPoint. Use a clean, modern tech theme (white, blue, dark grey).*

---

## Slide 1: Title Slide
**Headline:** Rethinking Candidate Discovery
**Sub-headline:** Beyond Keywords. Understanding Meaning, Trajectory, and Intent.
**Footer:** Built for the India Runs Data & AI Challenge | Team [Your Team Name]

---

## Slide 2: The Problem with Modern Recruiting
**Headline:** Keyword Matching is Broken
* **The Symptom:** Recruiters receive thousands of applications. ATS systems rank them by counting keywords.
* **The Result:** 
  * "Keyword stuffers" (candidates who paste the JD into their resume) rank at the top.
  * True experts (who describe their actual complex work) get buried.
* **The Goal:** Build a system that ranks candidates the way an expert human recruiter would.

---

## Slide 3: Our Approach
**Headline:** The 4 Pillars of Intelligent Ranking
Our engine doesn't just read words; it scores on four weighted axes:
1. **Semantic Competency (40%):** Does their experience actually map to the core competencies required? (e.g., matching "Weaviate" to the "Vector DB" cluster).
2. **Career Trajectory (30%):** Do they have promotion velocity? Are they coming from Tier-1 tech companies or pure consulting?
3. **Behavioral Intent (20%):** Are they actively looking? Do they actually respond to recruiters?
4. **Location Fit (10%):** Does their geography align with business needs?

---

## Slide 4: Anti-Gaming & Honeypot Detection
**Headline:** Defeating the "Keyword Stuffers"
We implemented robust anomaly detection to filter out fake or inflated profiles:
* **The "Instant Expert" Filter:** Flags profiles claiming "expert" proficiency in skills they've used for 0 months.
* **Experience Inconsistency:** Flags candidates claiming 10 years of experience but showing <1 year in their actual career history.
* **Shannon Entropy Analysis:** Statistically analyzes profile text. If a profile's text entropy deviates >2 standard deviations from the mean, it's flagged as an anomalous, likely machine-generated or keyword-stuffed profile.

---

## Slide 5: The Architecture
**Headline:** Lightning Fast. Fully Offline.
* **Backend Engine:** Pure Python. No heavy external dependencies.
* **Performance:** Processes 100,000+ candidate profiles in **under 35 seconds**.
* **Zero APIs:** Complies strictly with hackathon rules. Zero external LLM API calls during the ranking step to guarantee it runs within the 5-minute offline CPU limit.
* **Explainable AI (XAI):** Generates deterministic, human-readable rationale for *why* a candidate was ranked highly.

---

## Slide 6: The Judge's Dashboard (UI)
**Headline:** Beautiful, Interactive, and Transparent
*Instead of just submitting a CSV, we built a fully interactive dashboard.*
* **Zero Setup:** A pure HTML/JS application with zero build steps.
* **Features:** 
  * Configure the role (Skills, Exp, Location).
  * Upload the ranked CSV.
  * View deep scoring breakdowns with progress bars.
  * Search, sort, and export candidate data visually.
*(Insert a screenshot of your beautiful UI here!)*

---

## Slide 7: Conclusion & Impact
**Headline:** Hiring, Solved.
* **For Recruiters:** Reduces time-to-shortlist from days to 35 seconds.
* **For Candidates:** Rewards actual career growth and skill clusters, not just resume hacking.
* **For Redrob:** A production-ready, highly scalable heuristic engine that can be adapted to any job description via a simple JSON config.
**Footer:** Thank you! Check out our GitHub Repo.
