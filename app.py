import streamlit as st
import pandas as pd
import os
import sys
import time

# Import our backend logic
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from run import process_candidates

# --- Page Config ---
st.set_page_config(
    page_title="Redrob AI Ranker",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek Dark Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Animated Gradient Text */
    .main-header {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 5s linear infinite;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -1.5px;
    }
    
    @keyframes shine {
        to {
            background-position: 200% center;
        }
    }
    
    .sub-header {
        text-align: center;
        font-size: 1.5rem;
        color: #94a3b8;
        font-weight: 300;
        margin-bottom: 3.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Glassmorphism Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), border-color 0.4s ease;
        text-align: center;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-8px);
        border-color: rgba(129, 140, 248, 0.5);
        background: rgba(255, 255, 255, 0.05);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1.1rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 3rem;
        font-weight: 800;
        margin-top: 10px;
        text-shadow: 0 0 20px rgba(255,255,255,0.1);
    }
    
    /* Primary Button Styling */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        border: none;
        border-radius: 14px;
        padding: 12px 24px;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4);
    }
    
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 12px 30px rgba(147, 51, 234, 0.6);
    }
    
    /* Secondary Button Styling */
    button[data-testid="baseButton-secondary"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        color: #f8fafc;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Dataframe container */
    [data-testid="stDataFrame"] {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(10px);
    }
    
    /* File Uploader styling */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 40px;
        transition: all 0.4s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #818cf8;
        background: rgba(129, 140, 248, 0.05);
        transform: scale(1.01);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #f8fafc;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Layout ---
st.markdown('<h1 class="main-header">Redrob Intelligence</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Candidate Discovery & Ranking Engine</p>', unsafe_allow_html=True)

# Main container for centered content
col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])

with col_main:
    # Settings moved to expander to keep main UI clean and modern
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        limit = st.slider("Max Candidates to Rank", min_value=10, max_value=500, value=100, step=10)
        
    uploaded_file = st.file_uploader("Drop candidates.jsonl here to evaluate", type=['jsonl', 'json', 'gz'])

    if uploaded_file is not None:
        temp_path = os.path.join(os.getcwd(), "temp_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✨ Initiate Neural Ranking ✨", type="primary", use_container_width=True):
            with st.spinner("Analyzing semantic matches and behavioral signals..."):
                try:
                    start_time = time.time()
                    results = process_candidates(temp_path, limit=limit)
                    execution_time = time.time() - start_time
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                    st.toast('Analysis complete!', icon='✅')
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Metrics Display
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Candidates Shortlisted", f"{len(results)}")
                    m2.metric("Processing Time", f"{execution_time:.2f}s")
                    m3.metric("Honeypots Detected", "Active Check")
                    
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown("<h3 style='color: #f8fafc; font-weight: 600;'>🏆 Top Recommended Candidates</h3>", unsafe_allow_html=True)
                    
                    df = pd.DataFrame(results)
                    if not df.empty:
                        df = df[['rank', 'candidate_id', 'score', 'reasoning']]
                        
                        # Apply subtle styling to the dataframe
                        st.dataframe(
                            df, 
                            use_container_width=True,
                            height=600,
                            hide_index=True,
                            column_config={
                                "rank": st.column_config.NumberColumn("Rank", help="Candidate Rank"),
                                "candidate_id": st.column_config.TextColumn("Candidate ID"),
                                "score": st.column_config.NumberColumn("Score", format="%.4f"),
                                "reasoning": st.column_config.TextColumn("AI Reasoning", width="large")
                            }
                        )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Export Ranked CSV",
                            data=csv,
                            file_name='team_submission.csv',
                            mime='text/csv',
                            type="secondary",
                            use_container_width=True
                        )
                    else:
                        st.warning("No valid candidates found.")
                        
                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")
