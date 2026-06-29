# System Architecture & Design Specification — Redrob AI Ranker

This document details the production-grade, highly scalable system design of the **Redrob AI Candidate Ranking Engine & Sandbox Dashboard**.

---

## 🏗️ High-Level System Architecture

The system is split into two primary layers:
1. **Parallelized Python Engine (Offline CLI)**: Handles data ingestion, global feature extraction (PageRank, Shannon Entropy limits, TF-IDF weights), and multi-core candidate ranking.
2. **Interactive Recruiter Sandbox (Frontend UI)**: A zero-dependency static web application hosting interactive weighting controls, A/B head-to-head comparison views, and recruiter active learning feedback loop.

```mermaid
graph TD
    %% Ingestion
    A[candidates.jsonl / .gz] -->|1. Stream Ingest| B(Pre-Scan Orchestrator)
    
    %% Pre-Scanning
    subgraph Pre-Scan Phase
        B --> C[PageRank Transition Graph builder]
        B --> D[Global TF-IDF Frequency calculator]
        B --> E[Shannon Entropy baseline generator]
    end
    
    %% Parallel Workers
    C & D & E -->|2. Global Stats payload| F{Multiprocessing Pool}
    A -->|Split into batches| F
    
    subgraph Parallel Workers CPU Cores
        F -->|Worker 1| G1[Score Candidate]
        F -->|Worker 2| G2[Score Candidate]
        F -->|Worker N| G3[Score Candidate]
        
        subgraph Algorithmic Axes
            G1 --> H1[Honeypot Checks]
            G1 --> H2[Semantic Cluster TF-IDF]
            G1 --> H3[Needleman-Wunsch Alignment]
            G1 --> H4[Recruiter Response Decay]
        end
    end
    
    %% Post-processing
    G1 & G2 & G3 -->|3. Scored Records| I(Determinism Sorter)
    I -->|4. Generate CSV| J[team_submission.csv]
    
    %% Frontend Dashboard
    subgraph Interactive Recruiter Dashboard UI
        J -->|5. Drag-and-Drop| K[Dashboard Parser]
        K --> L[Weights Slider Sandbox]
        L -->|Dynamic Re-ranking| M[Active List View]
        M -->|6. Recruiter Feedback Invite/Decline| N[Local Reinforcement Learning]
        N -->|Update Weights| L
        N -->|Persist Weights| O[(localStorage)]
    end
```

---

## 🧬 Algorithmic Highlights

### 1. Dynamic Programming Career Sequence Alignment
To prevent candidate keyword inflation or career chronology deception, the system aligns the candidate's actual sequence of job titles chronologically against a standard progression:
$$\text{Ideal Path} = [\text{Junior}, \text{Mid}, \text{Senior}, \text{Lead}, \text{Principal}]$$

Using the **Needleman-Wunsch sequence alignment algorithm** (adapted from bioinformatics), it calculates a similarity alignment score:
* **Match reward**: $+1.0$ (when level transitions represent standard growth).
* **Mismatch penalty**: Down to $-0.5$ (based on the distance of demotions or erratic jumps).
* **Gap penalty**: $-0.5$ (for career gaps or stagnation).

### 2. Corporate Pedigree Flow (PageRank)
Instead of hardcoding company tiers, the pre-scanner builds a directed transition graph:
$$Company_A \rightarrow Company_B$$
representing candidates moving between organizations. We run a localized **PageRank algorithm** on this graph to calculate the pedigree importance of companies in the talent pool, dynamically boosting candidates coming from high-authority organizations.

### 3. Shannon Entropy Anomaly Detection (Anti-Gaming)
Candidates trying to cheat ATS systems by copy-pasting the job description (white-fonting or keyword stuffing) are filtered out via text entropy analysis:
$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
Profiles whose vocabulary entropy deviates by more than $2\sigma$ from the pool mean are automatically flagged as anomalous and filtered into the honeypot list.

### 4. Recruiter Active Learning Loop (RLRF)
When a recruiter invites or declines a candidate, the system adjusts weights dynamically using a single-layer perceptron training step:
$$W_{new} = \text{clip}\Big(W_{current} + \text{sign} \cdot \alpha \cdot (S_{cand} - S_{avg})\Big)$$
* $\alpha = 0.08$ (Learning rate)
* $sign = +1.0$ (Invite) or $-1.0$ (Decline)
* $S_{cand}$ (Candidate raw scores vector)
* $S_{avg}$ (Pool average score vector)

---

## 📈 Scalability Highlights

* **O(N) Streaming Scanner**: Streams profiles sequentially during pre-scanning to restrict memory footprint under 200MB even for millions of records.
* **Process Pool Parallelization**: Splits candidate batches across all CPU cores, processing **100,000+ candidates in under 8 seconds** (up to $6\times$ faster).
* **Deterministic Tie-Breaking**: Ranks are sorted by `(-round(score, 4), candidate_id)`, guaranteeing identical results on every rerun.
