import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

# MOVE PAGE CONFIG TO THE VERY TOP (Required by Streamlit)
st.set_page_config(page_title="Desktop Hygiene Monitor", layout="wide", page_icon="🛡️")

# --- CONFIGURATION ---
RISKY_KEYWORDS = ['password', 'secret', 'key', 'token', 'private', 'credential']
SIZE_LIMIT_MB = 50 

def apply_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        footer {visibility: hidden;}
        div[data-testid="stMetric"] {
            background-color: #1F2937; border: 1px solid #374151;
            padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        [data-testid="stMetricLabel"] { color: #9CA3AF; font-size: 14px; font-weight: 600; }
        [data-testid="stMetricValue"] { color: #FFFFFF; font-weight: bold; font-size: 28px; }
        h1 { color: #FFFFFF; font-weight: 800; letter-spacing: -0.5px; }
        h3 { color: #E5E7EB; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# Removed the docstring to look less "textbook"
def get_file_size_mb(size_bytes):
    return size_bytes / (1024 * 1024)

def scan_directory(directory_path):
    file_data = []
    IGNORED_FOLDERS = {'node_modules', '.git', '.venv', 'venv', '__pycache__', '.next', 'dist'}
    
    if not os.path.exists(directory_path):
        return None

    with st.spinner('🔍 Deep Scanning in progress... Analyzing file structure.'):
        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size_bytes = os.path.getsize(file_path)
                    size_mb = get_file_size_mb(size_bytes)
                    
                    risk_level = "Safe"
                    risk_reason = []
                    
                    # Check for risky keywords
                    file_lower = file.lower()
                    for keyword in RISKY_KEYWORDS:
                        if keyword in file_lower:
                            risk_level = "High"
                            risk_reason.append(f"Keyword: '{keyword}'")
                    
                    # Check for large files
                    if size_mb > SIZE_LIMIT_MB:
                        if risk_level == "Safe":
                            risk_level = "Medium"
                        risk_reason.append(f"Large ({size_mb:.1f} MB)")

                    file_data.append({
                        "File Name": file,
                        "Relative Path": os.path.relpath(file_path, directory_path),
                        "Size (MB)": round(size_mb, 2),
                        "Risk Level": risk_level,
                        "Issues": ", ".join(risk_reason) if risk_reason else "-"
                    })
                except (FileNotFoundError, PermissionError, OSError):
                    continue
    return file_data

def check_readme(directory_path):
    readme_path = os.path.join(directory_path, "README.md")
    return os.path.exists(readme_path)

# --- MAIN APP ---
apply_custom_css()

# Header
st.markdown("<h1>🛡️ Desktop Hygiene Monitor</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='color: #9CA3AF;'>IT Security & Storage Audit Dashboard</h5>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    target_dir = st.text_input("Target Directory", value=".", help="Enter the full path or use '.' for current directory")
    st.markdown("---")
    st.subheader("Audit Rules")
    st.markdown(f"**🚨 High Risk Keywords:** {', '.join(RISKY_KEYWORDS)}")
    st.markdown(f"**⚠️ Size Limit:** `{SIZE_LIMIT_MB} MB`")
    st.caption("Built for IT Audit & Compliance")

if st.button("🚀 Start Audit Scan", width='stretch'):
    data = scan_directory(target_dir)
    
    if data is None:
        st.error("❌ Directory not found. Please check the path.")
    else:
        df = pd.DataFrame(data)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(df))
        with col2:
            high_risk_count = len(df[df['Risk Level'] == 'High'])
            st.metric("🚨 High Risk Files", high_risk_count, delta_color="inverse")
        with col3:
            st.metric("Total Storage (MB)", f"{df['Size (MB)'].sum():.1f}")

        st.markdown("---")
        
        # README Check
        has_readme = check_readme(target_dir)
        col_doc1, col_doc2 = st.columns([1, 5])
        with col_doc1:
            if has_readme: st.success("✅ README")
            else: st.warning("⚠️ No README")
        with col_doc2:
            msg = "Project documentation detected." if has_readme else "Missing README.md. Add documentation for better maintainability."
            st.write(msg)

        st.markdown("---")
        
        # Charts
        col_chart, col_text = st.columns([1, 1])
        with col_chart:
            st.subheader("📊 Risk Distribution")
            risk_counts = df['Risk Level'].value_counts()
            fig, ax = plt.subplots(figsize=(5, 5))
            colors = {'High': '#EF4444', 'Medium': '#F59E0B', 'Safe': '#10B981'}
            labels = [risk_counts.index[i] for i in range(len(risk_counts))]
            sizes = risk_counts.values
            chart_colors = [colors.get(l, '#6B7280') for l in labels]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                                              colors=chart_colors, wedgeprops=dict(width=0.3, edgecolor='w'))
            centre_circle = plt.Circle((0,0),0.70,fc='#1F2937')
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')  
            for text in texts + autotexts:
                text.set_color('#FFFFFF')
                text.set_fontweight('bold')
            st.pyplot(fig, width='stretch')

        with col_text:
            st.subheader("🔥 Critical Alerts")
            high_risk_df = df[df['Risk Level'] == 'High']
            if not high_risk_df.empty:
                for index, row in high_risk_df.head(5).iterrows():
                    st.error(f"**{row['File Name']}**\n*{row['Relative Path']}*\n⚠️ {row['Issues']}")
            else:
                st.info("✨ No high-risk files found. Great hygiene!")

        st.markdown("---")
        st.subheader("📋 Full Audit Report")
        
        def highlight_risk(val):
            color = '#EF4444' if val == 'High' else '#F59E0B' if val == 'Medium' else '#10B981'
            return f'color: {color}; font-weight: bold;'

        styled_df = df.style.map(highlight_risk, subset=['Risk Level'])
        st.dataframe(styled_df, width='stretch', height=400)