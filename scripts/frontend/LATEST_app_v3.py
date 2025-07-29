import streamlit as st
import os
import json
import time
from PIL import Image
import re

st.set_page_config(
    page_title="KayG.ai",
    layout="wide",
    page_icon=":chart_with_upwards_trend:"
)

# --- FONT, STYLE, DROPDOWN, SCOPED BUTTON/CARD FIXES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"], .stApp {
        font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif !important;
        background: #FFFFFF !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown { color: #232323 !important; }
    .kpi-card:hover { box-shadow: 0 4px 24px rgba(50,120,180,0.09); transform: scale(1.025);}
    .vertical-picker label {font-weight:600; font-size:1.08rem;}
    div[data-baseweb="select"] > div { color: #232323 !important; font-weight: 600; }
    span.css-1wa3eu0-placeholder,
    .css-yk16xz-control, .css-1uccc91-singleValue { color: #232323 !important; }
    label, .vertical-picker label { color: #232323 !important; font-weight:600; }
    /* Strictly scoped Brainwave card style */
    .brainwave-card {
        background:linear-gradient(90deg,#E6FBF5 0,#E8F7FF 96%);
        box-shadow: 0 2px 18px rgba(30,168,180,0.07);
        border-radius: 16px; margin-bottom:1.2rem;
        padding:1.15rem 1.6rem 1.15rem 1.6rem;
        display:flex;flex-direction:column;justify-content:center;
    }
    .brainwave-card .brainwave-title {
        font-size:1.18rem;
        font-family:Inter,sans-serif;
        color:#12977C;
        font-weight:700;
        margin-bottom:.65rem;
    }
    .brainwave-card .brainwave-detail {
        font-size:15px;
        font-family:Inter,sans-serif;
        color:#191923;
    }
            
    /* --- Base Dropdown Styling --- */
    div[data-baseweb="select"] > div {
        border-radius: 12px;
        background: white;
        padding: 2px;
        border: 1px solid #E0E0E0;
        transition: all 0.4s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* --- Gradient Glow on Hover --- */
    div[data-baseweb="select"] > div:hover {
        background: linear-gradient(90deg, #f0f9ff, #e0f7fa);
        border: 1px solid transparent;
        box-shadow: 0 0 12px 2px rgba(0, 200, 255, 0.4),
                    0 0 18px 4px rgba(0, 150, 255, 0.2);
        transform: scale(1.015);
    }
    /* --- Gradient Text Highlight on Hover --- */
    div[data-baseweb="select"] > div:hover span {
        background: linear-gradient(to right, #007cf0, #00dfd8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
    }
    /* --- Rotate Caret Icon on Expand --- */
    div[data-baseweb="select"] svg {
        transition: transform 0.3s ease;
    }
    div[data-baseweb="select"][data-expanded="true"] svg {
        transform: rotate(180deg);
    }
    </style>
""", unsafe_allow_html=True)

# --- CARD HEIGHTS ---
kpi_card_height = "125px"
hot_card_height = "90px"

# --- HEADER ---
col1, col2 = st.columns([0.12, 0.88])
with col1:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.image(logo, width=150)
with col2:
    st.markdown(
        "<h1 style='font-family:Inter,sans-serif; font-size:2.05rem; "
        "font-weight:700; color:#1C3356; margin-bottom:0.05em;'>"
        "Market Intelligent Data Tool</h1>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='font-family:Inter,sans-serif; font-size:17px; "
        "color:#15607A; font-weight:500; margin-top:-8px; margin-bottom:0.1em;'>"
        "Cutting-edge executive insights at a glance</h3>", unsafe_allow_html=True)

st.markdown("---", unsafe_allow_html=True)

tabs = ["News Navigator", "Tab 2 (Coming Soon)", "Tab 3 (Coming Soon)"]
tab1, _, _ = st.tabs(tabs)

verticals = {
    "Agritech": "agritech",
    "AI Technology": "ai_technology",
    "Biotech": "biotech",
    "Cybersecurity": "cybersecurity",
    "Digital Health": "digital_health",
    "Electric Vehicles": "electric_vehicles",
    "Fintech": "fintech",
    "Green Energy": "green_energy",
    "Health Tech": "health_tech",
    "Space Tech": "space_tech"
}

KPI_ICONS = {
    "Funding / Investments": "💰",
    "Product Launch / Innovation": "🚀",
    "Partnerships / Collaborations": "🤝",
    "Mergers & Acquisitions": "🔀",
    "Regulatory / Compliance": "⚖️",
    "Market Share": "📈",
    "User Growth": "👥",
    "Revenue": "💸",
    "Profitability": "📊",
    "New Customers": "🧲",
    "Cost Optimization": "💡",
    "Patents Filed": "📝",
    "IPO / Listing": "🏆",
}
DEFAULT_ICON = "🔔"

with tab1:
    st.markdown('<div class="vertical-picker">', unsafe_allow_html=True)
    vertical_label = st.selectbox("Select Industry Vertical", list(verticals.keys()), index=0)
    st.markdown('</div>', unsafe_allow_html=True)
    vertical_key = verticals[vertical_label]
    digest_dir = os.path.join("outputs", "digest")
    kpi_path = os.path.join(digest_dir, f"{vertical_key}_kpi_table.json")
    entity_path = os.path.join(digest_dir, f"{vertical_key}_key_entities.txt")
    llm_path = os.path.join(digest_dir, f"{vertical_key}_llm_digest.txt")
    sources_path = os.path.join(digest_dir, f"{vertical_key}_kpi_sources.json")

    st.markdown(
        "<h2 style='font-family:Inter,sans-serif; font-size:1.28rem; font-weight:700; "
        "color:#1C3356;'>News Navigator</h2>",
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([1, 1.1], gap="large")

    # -------- VELOCITY BOARD KPIs (LEFT) --------
    with left_col:
        st.markdown(
            "<h2 style='font-family:Inter,sans-serif; font-size:1.28rem; font-weight:700; color:#1C3356;'>⚡ Velocity Board</h2>",
            unsafe_allow_html=True
        )
        st.caption(
            "<span style='font-family:Inter,sans-serif; font-size:1.01rem; color:#50506b;'>Key Metrics at a Glance</span>",
            unsafe_allow_html=True
        )
        kpi_sources = {}
        if os.path.exists(sources_path):
            try:
                with open(sources_path, "r", encoding="utf-8") as f:
                    for rec in json.load(f):
                        kpi_sources[rec["kpi"]] = rec.get("sources", [])
            except Exception:
                kpi_sources = {}
        if os.path.exists(kpi_path):
            with open(kpi_path, "r", encoding="utf-8") as f:
                kpis = json.load(f)
            card_per_row = 4
            card_rows = [kpis[i:i+card_per_row] for i in range(0, min(8, len(kpis)), card_per_row)]
            for row in card_rows:
                cols = st.columns(card_per_row, gap="small")
                for idx, card in enumerate(row):
                    kpi, value = card
                    icon = KPI_ICONS.get(kpi, DEFAULT_ICON)
                    sources = kpi_sources.get(kpi, [])
                    tooltip = "News Sources: " + "; ".join(sources) if sources else "Mentions in major news sources"
                    with cols[idx]:
                        st.markdown(
                            f"""
                            <div class="kpi-card" 
                                style="
                                    background: linear-gradient(90deg,#eaf6ff 0,#e0f5ee 100%);
                                    color: #222; border-radius: 14px;
                                    min-height: {kpi_card_height}; max-height: {kpi_card_height}; height: {kpi_card_height};
                                    width: 100%;
                                    display: flex; flex-direction: column; justify-content: space-between; align-items: center;
                                    font-family: 'Inter',sans-serif;
                                    padding: 0.72rem 0.93rem; margin-bottom:0.85rem;
                                    box-shadow: 0 2px 12px rgba(0,0,0,0.027);
                                    border: 1.2px solid #e3efed;
                                    transition: box-shadow .2s,transform .16s;
                                    overflow: hidden;"
                                title="{tooltip}">
                            <div style="font-size:18px; width:100%; text-align:center;">{icon}</div>
                            <div style='font-size:22px; font-weight:700; color:#126651; width:100%; text-align:center; margin: 5px 0 2px 0;'>
                                {value}
                            </div>
                            <div style='font-size:13px; font-weight:500; color:#177B5F; width:100%; text-align:center; margin-bottom:2px; line-height:1.20; white-space:normal; overflow:hidden;'>
                                {kpi}
                            </div>
                            </div>
                            """, unsafe_allow_html=True
                        )
        else:
            st.info("KPI data unavailable for this vertical.")

    # -------- HOT STREAKS (RIGHT) --------
    with right_col:
        st.markdown(
            "<h2 style='font-family:Inter,sans-serif; font-size:1.28rem; font-weight:700; color:#B55414;'>🔥 Hot Streaks</h2>",
            unsafe_allow_html=True
        )
        st.caption(
            "<span style='font-family:Inter,sans-serif; font-size:1.01rem; color:#4B2E1B;'>Entities, people, products making waves</span>",
            unsafe_allow_html=True
        )
        if os.path.exists(entity_path):
            with open(entity_path, "r", encoding="utf-8") as f:
                entities = [line.strip() for line in f.readlines() if line.strip()]
            hot_cols = st.columns(2, gap="small")
            for idx, ent in enumerate(entities):
                with hot_cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div style="
                            background:linear-gradient(90deg,#FFF6E6 0,#FDF2EC 95%);
                            color:#232323; border-left:5px solid #f48c06; border-radius:10px;
                            min-height: {hot_card_height};
                            max-height: {hot_card_height};
                            height: {hot_card_height};
                            display: flex; flex-direction: column; justify-content: center;
                            box-shadow: 0 1px 6px rgba(240,128,56,0.06); font-size:13px;
                            margin-bottom:.62rem; padding:.54rem .8rem;">
                        <span style="font-size:15px;padding-right:.34rem;">🔥</span>{ent}
                        </div>
                        """, unsafe_allow_html=True
                    )
        else:
            st.info("No highlight entity data for this vertical.")

# -------- BRAINWAVE SUMMARY (AI Digest, full width, free height, custom button style) --------
st.markdown("---")
st.markdown(
    "<h2 style='font-family:Inter,sans-serif; font-size:1.28rem; font-weight:700; color:#177B5F;'>🧠 Brainwave Summary</h2>",
    unsafe_allow_html=True
)
st.caption(
    "<span style='font-family:Inter,sans-serif; font-size:1.01rem; color:#26332e;'>Let our AI analyst make sense of it all</span>",
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .stSpinner > div > div {
        color: #177B5F !important;
        font-size: 1.09rem !important;
        font-family: 'Inter', 'Roboto', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# This div is the "marker" for button styling!

st.markdown('<div id="ai-recap-btn"></div>', unsafe_allow_html=True)

if "show_llm" not in st.session_state:
    st.session_state.show_llm = False

if not st.session_state.show_llm:
    if st.button("See AI Power Recap!", key="ai_power_button"):
        st.session_state.show_llm = True

if st.session_state.show_llm:
    with st.spinner("AI is reading all market bulletins and trends..."):
        time.sleep(1.5)
        if os.path.exists(llm_path):
            with open(llm_path, "r", encoding="utf-8") as f:
                llm_digest = f.read()
            def parse_llm_digest_sections(text):
                lines = text.splitlines()
                content_lines = []
                for l in lines:
                    if l.strip().startswith("- ") or l.strip().startswith("**"):
                        content_lines.append(l)
                    elif content_lines:
                        content_lines[-1] += " " + l
                text = "\n".join(content_lines).strip()
                bullet_pattern = r"-\s*\*\*(.+?)\*\*\:?\s*(.*?)(?=\s*-\s*\*\*|$)"
                matches = re.findall(bullet_pattern, text, flags=re.DOTALL)
                sections = []
                if matches:
                    for heading, detail in matches:
                        heading = heading.strip().replace(":", "")
                        detail = detail.strip().replace("\n", " ")
                        if heading and detail:
                            sections.append((heading, detail))
                    return sections
                block_pattern = r"\*\*(.+?)\*\*:?\s*(.*?)(?=(\*\*|$))"
                matches = re.findall(block_pattern, text, flags=re.DOTALL)
                for heading, detail, _ in matches:
                    heading = heading.strip().replace(":", "")
                    detail = detail.strip().replace("\n", " ")
                    if heading and detail:
                        sections.append((heading, detail))
                return sections
            cards = parse_llm_digest_sections(llm_digest)
            if not cards:
                st.warning("AI summary not properly formatted. Please check the LLM output.")
            row_cols = st.columns(3, gap="large")
            for idx, (heading, detail) in enumerate(cards):
                with row_cols[idx % 3]:
                    st.markdown(
                        f"""
                        <div class="brainwave-card">
                            <div class="brainwave-title">{heading}</div>
                            <div class="brainwave-detail">{detail}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
        else:
            st.info("No AI summary available for this vertical.")

st.markdown("""<hr style='margin-top:55px;margin-bottom:14px;border:1.5px solid #e0e9f9;'>""", unsafe_allow_html=True)
st.markdown("""
<p style='font-family:Inter,sans-serif;font-size:0.95rem;color:#666;margin-bottom:0px;margin-top:-12px;'>
    © 2025 <b>Market Intelligent Data Tool</b> &mdash; Built for strategy and speed
</p>
""", unsafe_allow_html=True)
