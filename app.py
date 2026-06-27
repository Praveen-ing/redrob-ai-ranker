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
    initial_sidebar_state="expanded"
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
    
    /* Vibrant Solid Sky Blue Header for 100% Visibility */
    .main-header {
        font-size: 4.5rem;
        font-weight: 800;
        color: #38bdf8 !important;
        text-align: center;
        letter-spacing: -1.5px;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    
    .sub-header {
        text-align: center;
        font-size: 1.5rem;
        color: #cbd5e1 !important; /* Lighter gray for readability */
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
        color: #cbd5e1 !important;
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
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        transition: all 0.4s ease !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #818cf8 !important;
        background: rgba(129, 140, 248, 0.05) !important;
        transform: scale(1.01) !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #818cf8 !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploadDropzone"] div,
    [data-testid="stFileUploadDropzone"] span {
        color: #cbd5e1 !important;
    }
    div[data-testid="stFileUploader"] label p {
        color: #f8fafc !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.02) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderHeader span, 
    .streamlit-expanderHeader p {
        color: #f8fafc !important;
    }
    
    /* Sidebar Text / Label Styling for High Contrast on Light Sidebar Background */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Scoring Weights Adjuster ---
st.sidebar.markdown("""
<div style='padding: 10px 0;'>
    <h2 style='font-family: Outfit; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;'>🎛️ Scorer Weights</h2>
    <p style='color: #94a3b8; font-size: 0.9rem;'>Fine-tune the ranking engine priorities on-the-fly</p>
</div>
""", unsafe_allow_html=True)

input_mode = st.sidebar.radio("Weight Input Mode", ["🎛️ Sliders (Auto-Normalized)", "✍️ Manual Percentage Input"])

if input_mode == "🎛️ Sliders (Auto-Normalized)":
    skills_w = st.sidebar.slider("Skills Score Weight", min_value=0, max_value=100, value=40, step=5)
    exp_w = st.sidebar.slider("Experience Weight", min_value=0, max_value=100, value=30, step=5)
    beh_w = st.sidebar.slider("Behavioral Weight", min_value=0, max_value=100, value=20, step=5)
    loc_w = st.sidebar.slider("Location Weight", min_value=0, max_value=100, value=10, step=5)

    # Calculate sum and normalize
    total_w = skills_w + exp_w + beh_w + loc_w

    if total_w > 0:
        norm_skills = (skills_w / total_w) * 100
        norm_exp = (exp_w / total_w) * 100
        norm_beh = (beh_w / total_w) * 100
        norm_loc = (loc_w / total_w) * 100
    else:
        norm_skills, norm_exp, norm_beh, norm_loc = 40.0, 30.0, 20.0, 10.0
    
    weights_valid = True
else:
    skills_w = st.sidebar.number_input("Skills Score Weight (%)", min_value=0, max_value=100, value=40, step=1)
    exp_w = st.sidebar.number_input("Experience Weight (%)", min_value=0, max_value=100, value=30, step=1)
    beh_w = st.sidebar.number_input("Behavioral Weight (%)", min_value=0, max_value=100, value=20, step=1)
    loc_w = st.sidebar.number_input("Location Weight (%)", min_value=0, max_value=100, value=10, step=1)

    total_w = skills_w + exp_w + beh_w + loc_w
    norm_skills, norm_exp, norm_beh, norm_loc = skills_w, exp_w, beh_w, loc_w
    
    weights_valid = (total_w == 100)

custom_weights = {
    'skills': norm_skills,
    'experience': norm_exp,
    'behavioral': norm_beh,
    'location': norm_loc
}

# Display effective normalized weights in sidebar
st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='color: #f8fafc; font-size: 1.1rem; font-weight: 600;'>⚖️ Effective Weights</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"🎯 **Skills:** `{norm_skills:.1f}%` *(Default: 40%)*")
st.sidebar.markdown(f"📈 **Experience:** `{norm_exp:.1f}%` *(Default: 30%)*")
st.sidebar.markdown(f"🤝 **Behavioral:** `{norm_beh:.1f}%` *(Default: 20%)*")
st.sidebar.markdown(f"📍 **Location:** `{norm_loc:.1f}%` *(Default: 10%)*")

if input_mode == "🎛️ Sliders (Auto-Normalized)":
    if total_w > 0:
        st.sidebar.caption("💡 Sliders are automatically normalized to sum to 100%.")
    else:
        st.sidebar.warning("⚠️ All weights are zero. Using default configuration.")
else:
    if weights_valid:
        st.sidebar.success("✅ Sum of weights is exactly 100%!")
    else:
        st.sidebar.error(f"❌ Weights must sum to 100% (Current sum: {total_w}%)")

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

    if not weights_valid:
        st.error(f"⚠️ Ranking is disabled because manual weights sum to {total_w}%. Please adjust them to sum to exactly 100% in the sidebar.")

    if uploaded_file is not None:
        temp_path = os.path.join(os.getcwd(), "temp_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✨ Initiate Neural Ranking ✨", type="primary", use_container_width=True, disabled=not weights_valid):
            with st.spinner("Analyzing semantic matches and behavioral signals..."):
                try:
                    start_time = time.time()
                    st.info(f"🚀 Running ranking algorithm (TF-IDF Rarity Weighting, Half-Life Activity Decay, and Career Velocity Gradient) with weights: Skills={norm_skills:.1f}%, Experience={norm_exp:.1f}%, Behavioral={norm_beh:.1f}%, Location={norm_loc:.1f}%")
                    results = process_candidates(temp_path, limit=limit, custom_weights=custom_weights)
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
