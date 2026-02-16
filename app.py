import streamlit as st
import base64
from logic import analyze_batch, get_parameter_names, save_comprehensive_pdf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Water Quality Analysis System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
if 'batch_list' not in st.session_state:
    st.session_state.batch_list = []
if 'show_report' not in st.session_state:
    st.session_state.show_report = False
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Initialize input defaults
if 'input_param' not in st.session_state: st.session_state.input_param = get_parameter_names()[0]
if 'input_val' not in st.session_state: st.session_state.input_val = 0.0

# --- THEME LOGIC ---
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# --- COLORS & ASSETS ---
if st.session_state.theme == 'light':
    bg_color = "#F0F2F6"
    card_bg = "#FFFFFF"
    text_color = "#111827"     # Darker Black for better visibility in Light Mode
    border_color = "#9CA3AF"
    input_bg = "#FFFFFF"       
    subtext_color = "#4B5563"
    header_bg = "linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)"
    stat_box_bg = "#F0FDFA"
    stat_box_border = "#CCFBF1"
else:
    bg_color = "#0E1117"
    card_bg = "#1F2937" 
    text_color = "#F9FAFB"
    border_color = "#4B5563"
    input_bg = "#111827"       
    subtext_color = "#D1D5DB"
    header_bg = "linear-gradient(135deg, #111827 0%, #1F2937 100%)"
    stat_box_bg = "#134E4A"
    stat_box_border = "#0F766E"

# EMBEDDED SVG LOGO
svg_logo = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M50 15 L55 5 L65 5 L70 15 L80 18 L90 10 L95 15 L88 25 L92 35 L100 40 L100 50 L92 55 L88 65 L95 75 L90 80 L80 72 L70 75 L65 85 L55 85 L50 75 L45 85 L35 85 L30 75 L20 72 L10 80 L5 75 L12 65 L8 55 L0 50 L0 40 L8 35 L12 25 L5 15 L10 10 L20 18 L30 15 L35 5 L45 5 L50 15 Z" fill="none" stroke="white" stroke-width="3"/>
  <path d="M50 25 Q30 55 30 70 A20 20 0 0 0 70 70 Q70 55 50 25 Z" fill="white" stroke="none"/>
</svg>
"""
logo_b64 = base64.b64encode(svg_logo.encode()).decode()

# --- CSS STYLING ---
st.markdown(f"""
<style>
    /* 1. GLOBAL LAYOUT */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
        overflow-x: hidden;
    }}
    [data-testid="stHeader"] {{ display: none; }}
    footer {{ display: none; }}

    .block-container {{
        max_width: 1000px;
        padding-top: 140px; 
        padding-bottom: 2rem;
    }}

    /* 2. FIXED HEADER */
    .header-container {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 120px;
        background: {header_bg};
        z-index: 99990;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        display: flex; justify-content: center;
    }}
    
    .header-inner {{
        width: 100%; max_width: 1000px; padding: 0 20px;
        display: flex; align-items: center; height: 100%;
        color: white; gap: 20px; position: relative;
    }}

    .logo-img {{ width: 60px; height: 60px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); }}
    .header-text {{ display: flex; flex-direction: column; }}
    .header-title {{ font-size: 1.8rem; font-weight: 800; margin: 0; line-height: 1.2; }}
    .header-subtitle {{ font-size: 0.9rem; font-weight: 300; opacity: 0.9; }}

    /* 3. THEME BUTTON (FIXED TOP RIGHT) */
    .theme-btn-wrapper {{
        position: fixed; top: 38px; right: 20px; z-index: 100000;
    }}
    
    .theme-btn-wrapper button {{
        background-color: rgba(255,255,255,0.15) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        width: 45px !important; height: 45px !important;
        padding: 0 !important; font-size: 1.2rem !important;
        border-radius: 50% !important;
    }}
    .theme-btn-wrapper button:hover {{
        background-color: rgba(255,255,255,0.3) !important;
        transform: scale(1.05);
    }}

    /* 4. FOOTER (DEFAULT: SCROLLING/NOT FIXED for Desktop) */
    .footer-container {{
        width: 100vw;
        position: relative;
        left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        background: {header_bg};
        color: white; 
        text-align: center; 
        padding: 20px;
        margin-top: 50px; 
        font-size: 0.8rem;
    }}

    /* 5. INPUT FIXES */
    /* Force Input Container Background */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
        background-color: {input_bg} !important;
        border: 1px solid {border_color} !important;
        color: {text_color} !important;
    }}
    /* Actual Input Tag */
    div[data-testid="stNumberInput"] input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        caret-color: {text_color} !important;
    }}
    /* Selectbox */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 1px solid {border_color} !important;
        color: {text_color} !important;
    }}
    /* Text/Icon Visibility Fix */
    .stSelectbox label, .stNumberInput label {{ color: {text_color} !important; font-weight: 600; }}
    div[data-baseweb="select"] span {{ color: {text_color} !important; }}
    
    /* FORCE ICONS DARK IN LIGHT MODE (Arrows, Steppers) */
    div[data-baseweb="select"] svg, div[data-testid="stNumberInput"] svg {{
        fill: {text_color} !important;
        color: {text_color} !important;
    }}

    /* 6. CARDS */
    .custom-card {{
        background-color: {card_bg};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid {border_color};
        color: {text_color};
    }}
    .card-title {{ font-size: 1.2rem; font-weight: 700; color: #3B82F6; margin-bottom: 5px; }}
    .card-subtitle {{ font-size: 0.85rem; color: {subtext_color}; margin-bottom: 15px; }}
    
    div[data-testid="stButton"] > button {{ border-radius: 8px !important; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #FF4B4B !important; color: white !important; border: none; }}

    /* 7. MOBILE OPTIMIZATION */
    @media (max-width: 600px) {{
        .header-container {{ height: 90px; }}
        .logo-img {{ width: 40px; height: 40px; }}
        .header-title {{ font-size: 1.1rem; }}
        .header-subtitle {{ font-size: 0.7rem; }}
        
        .theme-btn-wrapper {{ top: 22px; right: 15px; width: 35px; height: 35px; }}
        .theme-btn-wrapper button {{ width: 35px !important; height: 35px !important; font-size: 1rem !important; }}
        
        /* FOOTER FIXED ON MOBILE ONLY */
        .footer-container {{
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            margin: 0 !important;
            width: 100% !important;
            z-index: 99999 !important;
            padding: 10px !important;
        }}
        .footer-extra {{ display: none; }}
        
        /* Adjust padding so content doesn't hide behind fixed footer */
        .block-container {{ 
            padding-top: 110px; 
            padding-bottom: 80px !important; 
        }}

        /* Horizontal List on Mobile */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 5px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(1) {{ flex: 2 !important; min-width: 0 !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(2) {{ flex: 1 !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(3),
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(4) {{ flex: 0 0 35px !important; min-width: 35px !important; }}
        [data-testid="stVerticalBlockBorderWrapper"] p {{ font-size: 0.8rem !important; }}
    }}

    /* RESULT CARDS */
    .result-card {{ border: 1px solid {border_color}; border-radius: 8px; overflow: hidden; margin-bottom: 10px; background: {card_bg}; color: {text_color}; }}
    .result-header {{ background: #0284C7; color: white; padding: 10px 15px; font-weight: 600; display: flex; justify-content: space-between; }}
    .result-body {{ padding: 15px; display: flex; gap: 10px; flex-wrap: wrap; }}
    .standard-box {{ flex: 1; background: {bg_color}; padding: 8px; border-radius: 6px; border: 1px solid {border_color}; min-width: 150px; color: {text_color}; }}
    .status-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-top: 4px; color: #1F2937; }}
    .status-pass {{ background: #DCFCE7; color: #166534; }}
    .status-fail {{ background: #FEE2E2; color: #991B1B; }}
    .health-box {{ margin-top: 10px; background: #F0FDF4; border: 1px solid #BBF7D0; padding: 10px; border-radius: 6px; color: #166534; font-size: 0.85rem; }}
    .health-box-fail {{ background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; }}
    .summary-container {{ display: flex; justify-content: space-around; text-align: center; padding: 15px; background: {stat_box_bg}; border-radius: 12px; margin-top: 15px; border: 1px solid {stat_box_border}; color: {text_color}; }}
    .stat-number {{ font-size: 1.5rem; font-weight: 800; color: #0D9488; }}
    .stat-label {{ font-size: 0.7rem; text-transform: uppercase; color: {subtext_color}; }}
    
    [data-testid="stVerticalBlockBorderWrapper"] > div {{ border-color: {border_color} !important; }}
</style>
""", unsafe_allow_html=True)

# --- HEADER (FIXED) ---
st.markdown(f"""
<div class="header-container">
    <div class="header-inner">
        <img class="logo-img" src="data:image/svg+xml;base64,{logo_b64}"/>
        <div class="header-text">
            <div class="header-title">Water Quality System</div>
            <div class="header-subtitle">Professional Civil Engineering Platform</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- THEME BUTTON (FIXED TOP RIGHT) ---
st.markdown('<div class="theme-btn-wrapper">', unsafe_allow_html=True)
btn_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
st.button(btn_icon, on_click=toggle_theme, key="theme_toggle_btn")
st.markdown('</div>', unsafe_allow_html=True)

# --- CALLBACKS ---
def add_item_callback():
    p = st.session_state.input_param
    v = st.session_state.input_val
    if any(x['name'] == p for x in st.session_state.batch_list):
        st.toast(f"⚠️ {p} is already in the list!", icon="⚠️")
    else:
        st.session_state.batch_list.append({"name": p, "value": v})
        st.session_state.input_val = 0.0 
        st.session_state.show_report = False

def delete_item_callback(index):
    st.session_state.batch_list.pop(index)
    st.session_state.show_report = False

def edit_item_callback(index):
    item = st.session_state.batch_list[index]
    st.session_state.input_param = item['name']
    st.session_state.input_val = item['value']
    st.session_state.batch_list.pop(index)
    st.session_state.show_report = False

def show_report_callback():
    st.session_state.show_report = True

# --- INPUT CARD ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Add Parameter</div>', unsafe_allow_html=True)
st.markdown('<div class="card-subtitle">Select parameter and enter lab value</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    st.selectbox("Parameter Type", get_parameter_names(), key="input_param")
with c2:
    st.number_input("Measured Value", step=0.1, key="input_val")
with c3:
    st.write("") 
    st.write("") 
    st.button("＋ Add", on_click=add_item_callback, type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LIST CARD ---
if st.session_state.batch_list:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">Test Parameters ({len(st.session_state.batch_list)})</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Review items before analysis</div>', unsafe_allow_html=True)

    for i, item in enumerate(st.session_state.batch_list):
        with st.container(border=True):
            col_a, col_b, col_c, col_d = st.columns([3, 2, 0.5, 0.5])
            with col_a:
                st.markdown(f"**{item['name']}**")
            with col_b:
                st.markdown(f"{item['value']}") 
            with col_c:
                st.button("✏️", key=f"edit_{i}", on_click=edit_item_callback, args=(i,))
            with col_d:
                st.button("🗑️", key=f"del_{i}", on_click=delete_item_callback, args=(i,))

    st.write("")
    st.button("⟳ Run Analysis", type="primary", use_container_width=True, on_click=show_report_callback)
    st.markdown('</div>', unsafe_allow_html=True)

# --- REPORT CARD ---
if st.session_state.show_report and st.session_state.batch_list:
    gui_text, pdf_data = analyze_batch(st.session_state.batch_list)
    
    st.markdown('<div class="custom-card" style="border-top: 4px solid #10B981;">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Analysis Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Evaluation based on international standards</div>', unsafe_allow_html=True)

    total_params = len(pdf_data)
    safe_params = sum(1 for p in pdf_data if all(s['status'] != 'FAIL' for s in p['standards']))
    unsafe_params = total_params - safe_params

    for res in pdf_data:
        param_name = res['parameter']
        measured_val = res['value']
        
        standards_html = ""
        health_impact_html = ""
        is_safe_overall = True
        
        for std in res['standards']:
            status_class = "status-pass" if std['status'] != "FAIL" else "status-fail"
            status_text = "Pass" if std['status'] != "FAIL" else "Fail"
            
            if std['status'] == "FAIL":
                is_safe_overall = False
                health_impact_html += f"<div style='margin-bottom:6px;'><strong>⚠️ {std['authority']} Warning:</strong> {std.get('consequence', 'Risk detected.')}</div>"
                health_impact_html += f"<div><strong>🛠️ Suggested Solution:</strong> {std.get('solution', 'Consult civil engineer.')}</div>"
            
            standards_html += f"""<div class="standard-box"><div style="font-size:0.75rem; opacity:0.8;">{std['authority']}</div><div style="font-weight:600; font-size:0.9rem;">Limit: {std['limit']}</div><div class="status-badge {status_class}">{status_text}</div></div>"""
        
        if is_safe_overall:
            health_impact_html = "<div>Water clarity meets safety standards.</div>"
            health_box_class = "health-box"
        else:
            health_box_class = "health-box health-box-fail"

        card_html = f"""
<div class="result-card">
<div class="result-header">
<span>{param_name}</span>
<span style="font-weight:400; font-size:0.9rem;">{measured_val}</span>
</div>
<div class="result-body">
{standards_html}
</div>
<div style="padding: 0 15px 15px 15px;">
<div class="{health_box_class}">
{health_impact_html}
</div>
</div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-container">
        <div>
            <div class="stat-number" style="color:#3B82F6">{total_params}</div>
            <div class="stat-label">Total</div>
        </div>
        <div>
            <div class="stat-number" style="color:#10B981">{safe_params}</div>
            <div class="stat-label">Safe</div>
        </div>
        <div>
            <div class="stat-number" style="color:#EF4444">{unsafe_params}</div>
            <div class="stat-label">Risky</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 

    pdf_file = save_comprehensive_pdf(pdf_data)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📄 Download PDF",
            data=f,
            file_name="Water_Analysis_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer-container">
    <span>Analysis based on WHO & NAFDAC Standards</span>
    <span class="footer-extra"><br>For professional consultation, contact a certified laboratory</span>
</div>
""", unsafe_allow_html=True)