"""Streamlit UI utilities — reusable components and styling."""

import streamlit as st
from config.settings import THEME


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600;700&family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background:{THEME['bg']}; color:{THEME['text']}; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background:{THEME['panel']} !important;
    border-right: 1px solid {THEME['border']};
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background:{THEME['panel']};
    border-radius:10px;
    padding:4px;
    gap:4px;
    border-bottom: none;
}}
.stTabs [data-baseweb="tab"] {{
    font-family:'IBM Plex Mono', monospace;
    font-size:.72rem;
    letter-spacing:1px;
    text-transform:uppercase;
    border-radius:7px;
    color:{THEME['muted']};
    padding:8px 18px;
}}
.stTabs [aria-selected="true"] {{
    background:{THEME['bg']} !important;
    color:{THEME['accent']} !important;
}}

/* Buttons */
.stButton>button {{
    background: linear-gradient(135deg, {THEME['accent2']}, #5b21b6);
    color:white; border:none; border-radius:9px;
    font-family:'IBM Plex Mono',monospace; font-weight:700;
    font-size:.8rem; letter-spacing:.5px;
    padding:10px 24px; transition:all .2s;
    box-shadow: 0 4px 15px {THEME['accent2']}33;
}}
.stButton>button:hover {{
    transform:translateY(-1px);
    box-shadow: 0 6px 20px {THEME['accent2']}55;
}}

/* Cards */
.kpi-card {{
    background:{THEME['panel']};
    border:1px solid {THEME['border']};
    border-radius:14px;
    padding:20px 24px;
    text-align:center;
    position:relative;
    overflow:hidden;
    transition: transform .2s, box-shadow .2s;
}}
.kpi-card:hover {{
    transform:translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,212,255,.1);
}}
.kpi-card::before {{
    content:'';
    position:absolute; top:0; left:0; right:0;
    height:3px;
    background:linear-gradient(90deg, {THEME['accent']}, {THEME['accent2']});
}}
.kpi-value {{
    font-family:'Syne',sans-serif;
    font-size:2rem; font-weight:800;
    margin:8px 0 4px;
}}
.kpi-label {{
    font-size:.68rem; color:{THEME['muted']};
    text-transform:uppercase; letter-spacing:2px;
}}
.kpi-delta {{
    font-size:.75rem; margin-top:4px;
}}

/* Chat bubbles */
.chat-user {{
    background:linear-gradient(135deg, {THEME['accent2']}, #5b21b6);
    border-radius:16px 16px 4px 16px;
    padding:14px 18px; margin:10px 0 10px auto;
    max-width:80%; font-size:.88rem; color:white;
    box-shadow: 0 4px 15px {THEME['accent2']}33;
}}
.chat-ai {{
    background:{THEME['panel']};
    border:1px solid {THEME['border']};
    border-radius:16px 16px 16px 4px;
    border-left:3px solid {THEME['accent']};
    padding:14px 18px; margin:10px auto 10px 0;
    max-width:85%; font-size:.88rem; line-height:1.75;
}}
.chat-sql {{
    background:#0d1117;
    border:1px solid {THEME['border']};
    border-left:3px solid {THEME['accent3']};
    border-radius:0 8px 8px 0;
    padding:12px 16px; margin:8px 0;
    font-family:'IBM Plex Mono',monospace;
    font-size:.8rem; color:{THEME['accent3']};
    overflow-x:auto;
}}

/* File badge */
.file-badge {{
    background:{THEME['border']};
    border:1px solid #334155;
    border-radius:8px; padding:5px 12px;
    font-size:.72rem; display:inline-block; margin:3px;
    font-family:'IBM Plex Mono',monospace;
}}
.table-badge {{
    background:{THEME['accent']}15;
    border:1px solid {THEME['accent']}33;
    border-radius:6px; padding:4px 10px;
    font-size:.7rem; display:inline-block; margin:3px;
    color:{THEME['accent']};
    font-family:'IBM Plex Mono',monospace;
}}

/* Section headers */
.section-header {{
    font-family:'Syne',sans-serif;
    font-size:1.1rem; font-weight:800;
    color:{THEME['text']};
    margin:24px 0 12px;
    display:flex; align-items:center; gap:10px;
}}
.section-header::after {{
    content:'';
    flex:1; height:1px;
    background:linear-gradient(90deg, {THEME['border']}, transparent);
}}

/* Status dot */
.status-online {{ color:{THEME['accent3']}; }}
.status-offline {{ color:{THEME['danger']}; }}

/* Info box */
.info-box {{
    background:{THEME['accent']}0d;
    border:1px solid {THEME['accent']}33;
    border-radius:10px; padding:14px 18px;
    font-size:.85rem; margin:10px 0;
}}
.warn-box {{
    background:{THEME['warn']}0d;
    border:1px solid {THEME['warn']}33;
    border-radius:10px; padding:14px 18px;
    font-size:.85rem; margin:10px 0;
}}

/* Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {{
    background:{THEME['panel']} !important;
    border:1px solid {THEME['border']} !important;
    border-radius:9px !important;
    color:{THEME['text']} !important;
    font-family:'Inter',sans-serif !important;
}}
.stSelectbox>div>div {{
    background:{THEME['panel']} !important;
    border:1px solid {THEME['border']} !important;
    border-radius:9px !important;
}}

/* File uploader */
div[data-testid="stFileUploader"] {{
    background:{THEME['panel']};
    border:2px dashed {THEME['border']};
    border-radius:14px; padding:20px;
    transition: border-color .2s;
}}
div[data-testid="stFileUploader"]:hover {{
    border-color:{THEME['accent']};
}}

/* DataFrame */
.stDataFrame {{ border-radius:10px; overflow:hidden; }}

/* Expander */
.streamlit-expanderHeader {{
    background:{THEME['panel']} !important;
    border-radius:9px !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:.8rem !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-thumb {{ background:{THEME['border']}; border-radius:3px; }}

/* AI badge */
.ai-badge {{
    background:{THEME['accent3']}15;
    border:1px solid {THEME['accent3']}33;
    color:{THEME['accent3']};
    border-radius:20px; padding:3px 12px;
    font-size:.68rem; font-weight:700; letter-spacing:1px;
    font-family:'IBM Plex Mono',monospace;
}}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def kpi_card(col, label: str, value: str, color: str = THEME["accent"], delta: str = ""):
    delta_html = f"<div class='kpi-delta' style='color:{color}'>{delta}</div>" if delta else ""
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value' style='color:{color}'>{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)


def section_header(title: str, icon: str = ""):
    st.markdown(f"<div class='section-header'>{icon} {title}</div>", unsafe_allow_html=True)


def file_badge(name: str):
    return f"<span class='file-badge'>📄 {name}</span>"


def table_badge(name: str):
    return f"<span class='table-badge'>⬡ {name}</span>"


def chat_bubble_user(text: str):
    st.markdown(f"<div class='chat-user'>{text}</div>", unsafe_allow_html=True)


def chat_bubble_ai(text: str):
    # Convert markdown bold/bullets to HTML
    html = text.replace("\n", "<br>").replace("**", "<b>", 1)
    while "**" in html:
        html = html.replace("**", "</b>", 1) if html.count("**") % 2 == 0 else html.replace("**", "<b>", 1)
    st.markdown(f"<div class='chat-ai'>{text}</div>", unsafe_allow_html=True)


def sql_block(sql: str):
    st.markdown(f"<div class='chat-sql'>🔍 SQL<br>{sql}</div>", unsafe_allow_html=True)


def info_box(text: str):
    st.markdown(f"<div class='info-box'>ℹ️ {text}</div>", unsafe_allow_html=True)


def warn_box(text: str):
    st.markdown(f"<div class='warn-box'>⚠️ {text}</div>", unsafe_allow_html=True)
