import streamlit as st
import streamlit.components.v1 as components
import time
import random
import math
import json
import os
import tempfile
from dotenv import load_dotenv

from extract_text import extract_and_clean
from jd_function import call_llama_70b as extract_jd_data
from resume_function import call_llama_70b as extract_resume_data
from embed_out import run_matching_pipeline

load_dotenv()

st.set_page_config(
    page_title="Glass-Box Recruiter",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

defaults = {"result": None, "reset_key": 0, "dark_mode": True}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

dm = st.session_state.dark_mode

if dm:
    T = {
        "bg":            "#07090F",
        "surface":       "#0D1117",
        "surface2":      "#111827",
        "surface3":      "#161F2E",
        "border":        "#1E2D3D",
        "border2":       "#243550",
        "text":          "#E6EDF4",
        "text2":         "#6E8CAA",
        "text3":         "#38506A",
        "accent":        "#3B82F6",
        "accent2":       "#6366F1",
        "accent_glow":   "rgba(59,130,246,0.18)",
        "accent2_glow":  "rgba(99,102,241,0.14)",
        "page_glow":     "rgba(59,130,246,0.06)",
        "shadow":        "rgba(0,0,0,0.6)",
        "req_text":      "#60A5FA",   "req_bg":   "#0C1B30",  "req_border":  "#1C3D6A",
        "pref_text":     "#A78BFA",   "pref_bg":  "#130E25",  "pref_border": "#2D1F5E",
        "miss_text":     "#6E8CAA",   "miss_bg":  "#0D1117",  "miss_border": "#1E2D3D",
        "ev_req_accent": "#3B82F6",   "ev_pref_accent": "#7C3AED",
        "hi_text":       "#10B981",   "hi_bg":    "#041A10",  "hi_border":   "#0A3D22",
        "md_text":       "#F59E0B",   "md_bg":    "#1A1000",  "md_border":   "#3D2800",
        "lo_text":       "#F87171",   "lo_bg":    "#1A0505",  "lo_border":   "#3D1010",
        "input_bg":      "#0D1117",
        "btn_grad":      "linear-gradient(135deg, #1D4ED8 0%, #3B82F6 60%, #6366F1 100%)",
        "btn_dis_grad":  "linear-gradient(135deg, #141E2E, #1A2535)",
        "btn_dis_text":  "#2D4A6A",
        "badge_bg":      "linear-gradient(135deg,#0D1B2E,#131E35)",
        "badge_border":  "#1E3A5F",
        "badge_text":    "#60A5FA",
        "upload_ok":     "#34D399",
        "hint":          "#2D4A6A",
        "divider":       "#1E2D3D",
        "foot":          "#1C2D3E",
        "risk_text":     "#FCD34D",   "risk_bg":  "#1A1200",  "risk_border": "#3D2C00",
    }
else:
    T = {
        "bg":            "#F4F7FB",
        "surface":       "#FFFFFF",
        "surface2":      "#F8FAFF",
        "surface3":      "#EFF3FA",
        "border":        "#DDE5F0",
        "border2":       "#C8D5EA",
        "text":          "#0D1829",
        "text2":         "#4B6480",
        "text3":         "#8AA0BC",
        "accent":        "#2563EB",
        "accent2":       "#7C3AED",
        "accent_glow":   "rgba(37,99,235,0.12)",
        "accent2_glow":  "rgba(124,58,237,0.10)",
        "page_glow":     "rgba(37,99,235,0.04)",
        "shadow":        "rgba(15,30,60,0.08)",
        "req_text":      "#1D4ED8",   "req_bg":   "#EFF6FF",  "req_border":  "#BFDBFE",
        "pref_text":     "#6D28D9",   "pref_bg":  "#F5F3FF",  "pref_border": "#DDD6FE",
        "miss_text":     "#4B6480",   "miss_bg":  "#F8FAFF",  "miss_border": "#DDE5F0",
        "ev_req_accent": "#2563EB",   "ev_pref_accent": "#7C3AED",
        "hi_text":       "#059669",   "hi_bg":    "#ECFDF5",  "hi_border":   "#A7F3D0",
        "md_text":       "#D97706",   "md_bg":    "#FFFBEB",  "md_border":   "#FDE68A",
        "lo_text":       "#DC2626",   "lo_bg":    "#FEF2F2",  "lo_border":   "#FECACA",
        "input_bg":      "#F8FAFF",
        "btn_grad":      "linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #7C3AED 100%)",
        "btn_dis_grad":  "linear-gradient(135deg, #E2E8F0, #EFF3FA)",
        "btn_dis_text":  "#94A3B8",
        "badge_bg":      "linear-gradient(135deg,#EFF6FF,#EDE9FE)",
        "badge_border":  "#C7D2FE",
        "badge_text":    "#3730A3",
        "upload_ok":     "#059669",
        "hint":          "#8AA0BC",
        "divider":       "#DDE5F0",
        "foot":          "#C8D5EA",
        "risk_text":     "#B45309",   "risk_bg":  "#FFFBEB",  "risk_border": "#FDE68A",
    }

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&family=Figtree:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

*, html, body, [class*="css"] {{
  font-family: 'Figtree', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  box-sizing: border-box;
}}
.stApp {{
  background: {T['bg']} !important;
  background-image:
    radial-gradient(ellipse 80% 45% at 50% -5%, {T['page_glow']}, transparent),
    radial-gradient(ellipse 40% 30% at 85% 15%, rgba(99,102,241,0.035), transparent) !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
  padding-top: 0 !important;
  padding-bottom: 5rem !important;
  max-width: 860px !important;
}}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border2']}; border-radius: 99px; }}

div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: {T['surface']} !important;
  border: 1px solid {T['border']} !important;
  border-radius: 22px !important;
  padding: 2rem 2.2rem !important;
  box-shadow: 0 1px 2px {T['shadow']}, 0 6px 28px rgba(0,0,0,{0.14 if dm else 0.06}) !important;
  margin-bottom: 1.2rem !important;
  overflow: hidden;
}}

.hero {{ text-align: center; padding: 3.5rem 1rem 2.2rem; }}
.hero-badge {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: {T['badge_bg']}; color: {T['badge_text']};
  font-size: 0.62rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase;
  padding: 0.3rem 0.95rem; border-radius: 999px; border: 1px solid {T['badge_border']};
  margin-bottom: 1.1rem;
}}
.hero-title {{
  font-family: 'Bricolage Grotesque', sans-serif !important;
  font-size: 3.2rem; font-weight: 800;
  background: {"linear-gradient(135deg, #93C5FD 0%, #A5B4FC 55%, #C4B5FD 100%)" if dm
               else "linear-gradient(135deg, #1E293B 0%, #2563EB 55%, #7C3AED 100%)"};
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  line-height: 1.06; margin-bottom: 0.6rem; letter-spacing: -0.03em;
}}
.hero-sub {{ font-size: 0.97rem; color: {T['text2']}; font-weight: 400; }}

div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {{
  padding: 0.42rem 0.85rem !important; font-size: 0.74rem !important;
  border-radius: 9px !important; background: {T['surface2']} !important;
  color: {T['text2']} !important; border: 1px solid {T['border']} !important;
  box-shadow: none !important; font-weight: 500 !important; width: auto !important;
  letter-spacing: 0 !important;
}}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {{
  border-color: {T['accent']} !important; color: {T['accent']} !important;
  transform: none !important; box-shadow: none !important; filter: none !important;
}}

.flabel {{
  font-family: 'Bricolage Grotesque', sans-serif !important;
  font-size: 0.71rem; font-weight: 700; color: {T['text']};
  letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 0.28rem;
}}
.fhint {{ font-size: 0.77rem; color: {T['text3']}; margin-bottom: 0.5rem; }}

div[data-testid="stFileUploader"] {{
  background: {T['input_bg']} !important; border: 1.5px dashed {T['border2']} !important;
  border-radius: 13px !important; transition: border-color 0.2s;
}}
div[data-testid="stFileUploader"]:hover {{ border-color: {T['accent']} !important; }}
div[data-testid="stFileUploader"] label {{ display: none !important; }}

div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {{ display: none !important; }}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {{
  background: {T['input_bg']} !important; border: 1.5px solid {T['border']} !important;
  border-radius: 12px !important; color: {T['text']} !important;
  font-size: 0.9rem !important; font-weight: 400 !important; transition: all 0.2s;
}}
div[data-testid="stTextInput"] input {{ padding: 0.66rem 1rem !important; }}
div[data-testid="stTextArea"] textarea {{
  padding: 0.75rem 1rem !important; min-height: 136px !important; resize: vertical !important;
}}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {{
  border-color: {T['accent']} !important;
  box-shadow: 0 0 0 3px {T['accent_glow']} !important;
  background: {T['surface']} !important; outline: none !important;
}}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {{ color: {T['text3']} !important; }}

div[data-testid="stButton"] > button {{
  width: 100%; background: {T['btn_grad']} !important;
  color: #FFF !important; font-weight: 600 !important; font-size: 0.94rem !important;
  border: none !important; border-radius: 13px !important; padding: 0.86rem 2rem !important;
  box-shadow: 0 4px 18px rgba(59,130,246,0.28) !important;
  transition: all 0.2s ease !important; letter-spacing: 0.01em !important;
}}
div[data-testid="stButton"] > button:hover:not(:disabled) {{
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 28px rgba(59,130,246,0.38) !important;
  filter: brightness(1.07) !important;
}}
div[data-testid="stButton"] > button:disabled {{
  background: {T['btn_dis_grad']} !important; box-shadow: none !important;
  opacity: 0.7 !important; cursor: not-allowed !important; transform: none !important;
  color: {T['btn_dis_text']} !important;
}}

.divider {{ border: none; border-top: 1px solid {T['divider']}; margin: 1.5rem 0; }}
.upload-ok {{ font-size: 0.79rem; color: {T['upload_ok']}; font-weight: 600; margin-top: 0.3rem; }}
.hint {{ text-align:center; font-size:0.75rem; color:{T['hint']}; margin-top:0.5rem; }}
.gap {{ height: 1rem; }} .gap-sm {{ height: 0.5rem; }}

.results-banner {{
  display:flex; align-items:center; gap:0.7rem;
  margin-bottom:1.5rem; padding-bottom:1.1rem; border-bottom:1px solid {T['divider']};
}}
.live-dot {{
  width:9px; height:9px; border-radius:50%; background:#22C55E; flex-shrink:0;
  box-shadow:0 0 0 3px rgba(34,197,94,0.2); animation:dp 2.5s ease-in-out infinite;
}}
@keyframes dp {{
  0%,100%{{ box-shadow:0 0 0 3px rgba(34,197,94,0.2); }}
  50%    {{ box-shadow:0 0 0 7px rgba(34,197,94,0.06); }}
}}
.banner-title {{
  font-family:'Bricolage Grotesque',sans-serif !important;
  font-size:1.12rem; font-weight:700; color:{T['text']};
}}
.banner-sub {{ font-size:0.78rem; color:{T['text2']}; margin-top:0.07rem; }}

.sec-head {{
  display:flex; align-items:center; gap:0.5rem;
  font-family:'Bricolage Grotesque',sans-serif !important;
  font-size:0.7rem; font-weight:700; letter-spacing:0.13em; text-transform:uppercase;
  color:{T['text2']}; margin-bottom:0.9rem;
}}
.sec-line {{ flex:1; height:1px; background:{T['border']}; }}

.skill-cat-label {{
  font-size:0.65rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
  margin-bottom:0.55rem; margin-top:0.1rem; display:flex; align-items:center; gap:0.4rem;
}}
.skill-cat-label .cat-dot {{
  width:6px; height:6px; border-radius:50%; flex-shrink:0;
}}

.pill-row {{ display:flex; flex-wrap:wrap; gap:0.45rem; }}
.pill {{
  display:inline-flex; align-items:center; gap:0.38rem;
  font-size:0.83rem; font-weight:500; padding:0.38rem 0.82rem;
  border-radius:10px; cursor:pointer; text-decoration:none !important;
  transition:all 0.17s ease; line-height:1.2;
}}
.pill:hover {{ transform:translateY(-1px); box-shadow:0 3px 10px {T['shadow']}; }}
.pill.active {{ box-shadow:0 0 0 3px {T['accent_glow']}; }}

.pill-req {{
  background:{T['req_bg']}; color:{T['req_text']}; border:1px solid {T['req_border']};
}}
.pill-req:hover {{ border-color:{T['req_text']}; background:{T['req_bg']}; }}
.pill-req.active {{ border-color:{T['req_text']}; background:{T['req_bg']}; }}

.pill-pref {{
  background:{T['pref_bg']}; color:{T['pref_text']}; border:1px solid {T['pref_border']};
}}
.pill-pref:hover {{ border-color:{T['pref_text']}; background:{T['pref_bg']}; }}
.pill-pref.active {{ border-color:{T['pref_text']}; background:{T['pref_bg']}; }}

.pill-miss {{
  background:{T['miss_bg']}; color:{T['miss_text']}; border:1px dashed {T['miss_border']};
  opacity:0.75;
}}
.pill-miss:hover {{ opacity:1; border-style:solid; }}

.ev-box {{
  border-radius:0 12px 12px 12px;
  padding:1rem 1.1rem; margin:0.2rem 0 0.6rem 0;
  animation:si 0.17s ease;
}}
.ev-box-req {{ background:{T['req_bg']}; border:1px solid {T['req_border']}; border-left:3px solid {T['req_text']}; }}
.ev-box-pref {{ background:{T['pref_bg']}; border:1px solid {T['pref_border']}; border-left:3px solid {T['pref_text']}; }}
@keyframes si {{ from{{opacity:0;transform:translateY(-4px)}} to{{opacity:1;transform:translateY(0)}} }}
.ev-label {{
  font-family:'Bricolage Grotesque',sans-serif !important;
  font-size:0.64rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase;
  margin-bottom:0.55rem;
}}
.ev-label-req {{ color:{T['req_text']}; }}
.ev-label-pref {{ color:{T['pref_text']}; }}
.ev-text {{
  font-size:0.86rem; line-height:1.7; color:{T['text']};
  font-weight:400; white-space:pre-wrap;
}}

.item-card {{
  background:{T['surface2']}; border:1px solid {T['border']};
  border-radius:14px; padding:1rem 1.15rem; margin-bottom:0.48rem;
  cursor:pointer; display:block; width:100%; text-decoration:none !important;
  transition:all 0.17s ease; position:relative; box-sizing:border-box;
}}
.item-card:hover {{ border-color:{T['border2']}; box-shadow:0 4px 16px {T['shadow']}; background:{T['surface3']}; }}
.item-card.active {{ border-color:{T['accent']}; box-shadow:0 0 0 3px {T['accent_glow']}; background:{T['surface3']}; }}
.item-row {{ display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; }}
.item-name {{
  font-family:'Bricolage Grotesque',sans-serif !important;
  font-size:0.91rem; font-weight:600; color:{T['text']}; line-height:1.3;
}}
.item-sub {{ font-size:0.77rem; color:{T['text2']}; margin-top:0.17rem; }}
.item-right {{ display:flex; flex-direction:column; align-items:flex-end; gap:0.28rem; flex-shrink:0; }}
.item-meta {{ font-size:0.72rem; color:{T['text3']}; }}
.chev {{ font-size:0.6rem; color:{T['text3']}; transition:transform 0.2s; }}
.active .chev {{ transform:rotate(180deg); }}

.conf-dot {{
  width:8px; height:8px; border-radius:50%; flex-shrink:0; display:inline-block;
}}
.conf-dot-hi {{ background:{T['hi_text']}; box-shadow:0 0 0 2px {'rgba(16,185,129,0.18)' if dm else 'rgba(5,150,105,0.14)'}; }}
.conf-dot-md {{ background:{T['md_text']}; box-shadow:0 0 0 2px {'rgba(245,158,11,0.18)' if dm else 'rgba(217,119,6,0.14)'}; }}
.conf-dot-lo {{ background:{T['lo_text']}; box-shadow:0 0 0 2px {'rgba(248,113,113,0.18)' if dm else 'rgba(220,38,38,0.14)'}; }}
.conf-row {{ display:flex; align-items:center; gap:0.35rem; }}
.conf-label {{ font-size:0.7rem; font-weight:600; }}
.conf-label-hi {{ color:{T['hi_text']}; }}
.conf-label-md {{ color:{T['md_text']}; }}
.conf-label-lo {{ color:{T['lo_text']}; }}

.ev-box-std {{
  background:{T['surface3']}; border:1px solid {T['border']}; border-left:3px solid {T['accent']};
  border-radius:0 12px 12px 12px; padding:1rem 1.1rem; margin:0 0 0.5rem 0;
  animation:si 0.17s ease;
}}
.ev-label-std {{ color:{T['accent']}; font-family:'Bricolage Grotesque',sans-serif !important;
  font-size:0.64rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase;
  margin-bottom:0.6rem; }}

.risk-item {{
  display:flex; align-items:flex-start; gap:0.7rem;
  background:{T['risk_bg']}; border:1px solid {T['risk_border']};
  border-left:3px solid {T['risk_text']};
  border-radius:0 12px 12px 0;
  padding:0.82rem 1rem; margin-bottom:0.48rem; transition:transform 0.17s;
}}
.risk-item:hover {{ transform:translateX(3px); }}
.risk-icon {{ font-size:0.92rem; margin-top:0.06rem; flex-shrink:0; }}
.risk-text {{ font-size:0.86rem; color:{T['risk_text']}; font-weight:500; line-height:1.5; }}

.ev-accordion {{
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.28s cubic-bezier(0.4,0,0.2,1),
              opacity 0.22s ease,
              margin 0.22s ease;
  margin-top: 0;
  margin-bottom: 0;
}}
.ev-accordion.open {{
  max-height: 700px;
  opacity: 1;
  margin-top: 0.3rem;
  margin-bottom: 0.55rem;
}}
.pill.active {{ box-shadow: 0 0 0 3px {T['accent_glow']} !important; }}
.pill-req.active  {{ border-color:{T['req_text']} !important; }}
.pill-pref.active {{ border-color:{T['pref_text']} !important; }}
.item-card.active {{ border-color:{T['accent']}; box-shadow:0 0 0 3px {T['accent_glow']}; background:{T['surface3']}; }}
.item-card.active .chev {{ transform:rotate(180deg); display:inline-block; }}
.chev {{ display:inline-block; transition:transform 0.22s ease; }}
.pill-chev {{ font-size:0.55rem; margin-left:0.18rem; display:inline-block;
              transition:transform 0.22s ease; }}
.pill.active .pill-chev {{ transform:rotate(180deg); }}
.pill {{ cursor:pointer; user-select:none; }}
.item-card {{ cursor:pointer; user-select:none; }}

</style>
""", unsafe_allow_html=True)

CONF_LABELS = {"hi": "Verified", "md": "Partial", "lo": "Unverified"}

def conf_badge(level):
    dot_cls   = f"conf-dot conf-dot-{level}"
    label_cls = f"conf-label conf-label-{level}"
    return (
        f'<span class="conf-row">'
        f'<span class="{dot_cls}"></span>'
        f'<span class="{label_cls}">{CONF_LABELS[level]}</span>'
        f'</span>'
    )

SOURCE_STYLES = {
    "Resume":   lambda: (T['req_bg'],  T['req_text'],  T['req_border']),
    "GitHub":   lambda: (T['hi_bg'],   T['hi_text'],   T['hi_border']),
    "LinkedIn": lambda: (
        "rgba(14,165,233,0.08)" if dm else "#F0F9FF",
        "#38BDF8"               if dm else "#0369A1",
        "rgba(56,189,248,0.20)" if dm else "#BAE6FD",
    ),
}

def parse_evidence(text):
    rows = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            src, desc = line.split(":", 1)
            rows.append((src.strip(), desc.strip()))
        else:
            rows.append(("Note", line))
    return rows

def ev_card_html(item_id, text, cat="std"):
    rows = parse_evidence(text)
    n = len(rows)
    if n >= 3:
        conf_text = "Strong evidence based on multiple sources"
        conf_col  = T['hi_text']
    elif n == 2:
        conf_text = "Moderate evidence — two sources cross-referenced"
        conf_col  = T['md_text']
    else:
        conf_text = "Single source — additional verification recommended"
        conf_col  = T['lo_text']

    if cat == "req":
        accent = T['req_text'];  card_bg = T['req_bg'];   card_brd = T['req_border']
    elif cat == "pref":
        accent = T['pref_text']; card_bg = T['pref_bg'];  card_brd = T['pref_border']
    else:
        accent = T['accent'];    card_bg = T['surface3']; card_brd = T['border']

    src_html = ""
    for src, desc in rows:
        getter = SOURCE_STYLES.get(src)
        if getter:
            bg, col, brd = getter()
        else:
            bg, col, brd = T['surface3'], T['text2'], T['border']
        src_html += f"""
<div style="display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:0.55rem;">
  <span style="flex-shrink:0;font-size:0.59rem;font-weight:700;letter-spacing:0.1em;
               text-transform:uppercase;padding:0.18rem 0.52rem;border-radius:5px;
               background:{bg};color:{col};border:1px solid {brd};
               white-space:nowrap;margin-top:0.15rem;">{src}</span>
  <span style="font-size:0.84rem;color:{T['text']};line-height:1.65;">{desc}</span>
</div>"""

    return f"""
<div class="ev-accordion" id="ev-{item_id}">
  <div style="background:{card_bg};border:1px solid {card_brd};
              border-left:3px solid {accent};border-radius:0 12px 12px 12px;
              padding:0.9rem 1.05rem;overflow:hidden;">
    <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:0.63rem;
                font-weight:700;letter-spacing:0.13em;text-transform:uppercase;
                color:{accent};margin-bottom:0.75rem;">📎 Evidence</div>
    {src_html}
    <div style="margin-top:0.55rem;padding-top:0.5rem;
                border-top:1px solid {card_brd};
                font-size:0.75rem;font-weight:600;color:{conf_col};">
      ✓ &nbsp;{conf_text}
    </div>
  </div>
</div>"""

ACCORDION_COMPONENT_JS = """
<script>
(function() {
  var d = window.parent.document;

  function toggleEv(id) {
    var panel   = d.getElementById('ev-' + id);
    var trigger = d.querySelector('[data-ev="' + id + '"]');
    if (!panel) return;
    var isOpen = panel.classList.contains('open');

    d.querySelectorAll('.ev-accordion').forEach(function(p) {
      p.classList.remove('open');
    });
    d.querySelectorAll('[data-ev]').forEach(function(el) {
      el.classList.remove('active');
      var chev = el.querySelector('.chev, .pill-chev');
      if (chev) chev.style.transform = '';
    });

    if (!isOpen) {
      panel.classList.add('open');
      if (trigger) {
        trigger.classList.add('active');
        var chev = trigger.querySelector('.chev, .pill-chev');
        if (chev) chev.style.transform = 'rotate(180deg)';
      }
    }
  }

  window.parent.toggleEv = toggleEv;

  function attach() {
    d.querySelectorAll('[data-ev]').forEach(function(el) {
      if (!el._evBound) {
        el._evBound = true;
        el.addEventListener('click', function(e) {
          e.preventDefault();
          toggleEv(el.getAttribute('data-ev'));
        });
      }
    });
  }

  attach();
  setTimeout(attach, 300);
  setTimeout(attach, 900);
})();
</script>
"""

def render_skill_pill(item, cat):
    cls = f"pill pill-{cat}"
    return (
        f'<span class="{cls}" data-ev="{item["id"]}" '
        f'onclick="toggleEv(\'{item["id"]}\')">'
        f'{item["name"]}'
        f'<span class="pill-chev">&#9662;</span>'
        f'</span>'
    )

def render_missing_pill(item):
    return f'<span class="pill pill-miss">{item["name"]}</span>'

def item_card(item):
    return (
        f'<div class="item-card" data-ev="{item["id"]}" '
        f'onclick="toggleEv(\'{item["id"]}\')">'
        f'<div class="item-row">'
        f'  <div>'
        f'    <div class="item-name">{item["name"]}</div>'
        f'    <div class="item-sub">{item["sub"]}</div>'
        f'  </div>'
        f'  <div class="item-right">'
        f'    <span class="item-meta">{item["meta"]}</span>'
        f'    {conf_badge(item["level"])}'
        f'    <span class="chev">&#9662;</span>'
        f'  </div>'
        f'</div>'
        f'</div>'
    )

def sec_head(icon, title):
    return (
        f'<div class="sec-head">'
        f'{icon}&ensp;{title}'
        f'<span class="sec-line"></span>'
        f'</div>'
    )

def skill_cat_label(dot_color, border_color, text_color, label):
    return (
        f'<div class="skill-cat-label" style="color:{text_color};">'
        f'<span class="cat-dot" style="background:{dot_color};'
        f'box-shadow:0 0 0 2px {border_color};"></span>'
        f'{label}'
        f'</div>'
    )

def make_gauge(score, risks_count=0, n_req=0, n_pref=0, n_miss=0):
    if score >= 70:
        lbl_text   = "Strong Fit"
        dot_color  = "#3B82F6" if dm else "#1D4ED8"
        lbl_col    = "#60A5FA" if dm else "#1D4ED8"
        lbl_bg     = "rgba(59,130,246,0.10)" if dm else "rgba(37,99,235,0.07)"
        lbl_brd    = "rgba(59,130,246,0.26)" if dm else "rgba(37,99,235,0.20)"
    elif score >= 45:
        lbl_text   = "Moderate Fit"
        dot_color  = "#818CF8" if dm else "#4F46E5"
        lbl_col    = "#A78BFA" if dm else "#4338CA"
        lbl_bg     = "rgba(99,102,241,0.10)" if dm else "rgba(67,56,202,0.07)"
        lbl_brd    = "rgba(99,102,241,0.26)" if dm else "rgba(67,56,202,0.20)"
    else:
        lbl_text   = "Needs Review"
        dot_color  = "#38BDF8" if dm else "#0369A1"
        lbl_col    = "#38BDF8" if dm else "#0369A1"
        lbl_bg     = "rgba(56,189,248,0.08)" if dm else "rgba(3,105,161,0.06)"
        lbl_brd    = "rgba(56,189,248,0.24)" if dm else "rgba(3,105,161,0.18)"

    R        = 70
    SW       = 14
    CIRC     = round(2 * math.pi * R, 3)
    offset   = round(CIRC - (score / 100.0) * CIRC, 3)

    track    = "rgba(255,255,255,0.07)" if dm else "rgba(15,30,60,0.09)"
    num_col  = lbl_col
    sub_col  = T['text3']

    def stat_cell(val, key):
        return f"""
<div style="
  flex:1; text-align:center;
  background:{T['surface2']}; border:1px solid {T['border']};
  border-radius:12px; padding:0.7rem 0.5rem;
">
  <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.25rem;font-weight:800;
              color:{T['text']};line-height:1;">{val}</div>
  <div style="font-size:0.65rem;font-weight:600;letter-spacing:0.09em;text-transform:uppercase;
              color:{T['text3']};margin-top:0.25rem;">{key}</div>
</div>"""

    stats_html = (
        stat_cell(f"{n_req}/{n_req}", "Required") +
        stat_cell(f"{n_pref}/{n_pref}", "Preferred") +
        stat_cell(str(n_miss), "Missing") +
        stat_cell(str(risks_count), "Risk signals")
    )

    return f"""
<style>
@keyframes _ring_fill {{
  from {{ stroke-dashoffset: {CIRC}; }}
  to   {{ stroke-dashoffset: {offset}; }}
}}
@keyframes _num_up {{
  from {{ opacity:0; transform:translateY(5px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes _fade {{
  from {{ opacity:0; }} to {{ opacity:1; }}
}}
</style>

<div style="display:flex;flex-direction:column;align-items:center;gap:1.1rem;padding:1.2rem 0 0.4rem;">
  <div style="position:relative;width:196px;height:196px;flex-shrink:0;">
    <svg width="196" height="196" viewBox="0 0 196 196"
         xmlns="http://www.w3.org/2000/svg"
         style="position:absolute;top:0;left:0;">
      <defs>
        <linearGradient id="rg_{score}" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stop-color="#3B82F6"/>
          <stop offset="100%" stop-color="#818CF8"/>
        </linearGradient>
      </defs>
      <circle cx="98" cy="98" r="{R}"
        fill="none" stroke="{track}"
        stroke-width="{SW}" stroke-linecap="round"/>
      <circle cx="98" cy="98" r="{R - SW // 2 - 8}"
        fill="none"
        stroke="{'rgba(59,130,246,0.07)' if dm else 'rgba(37,99,235,0.05)'}"
        stroke-width="1"/>
      <circle cx="98" cy="98" r="{R}"
        fill="none"
        stroke="url(#rg_{score})"
        stroke-width="{SW}"
        stroke-linecap="round"
        stroke-dasharray="{CIRC}"
        stroke-dashoffset="{CIRC}"
        transform="rotate(-90 98 98)"
        style="animation:_ring_fill 1s cubic-bezier(0.34,1.20,0.64,1) 0.15s forwards;"/>
    </svg>
    <div style="
      position:absolute;inset:0;
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      animation:_num_up 0.5s ease 0.4s both;
    ">
      <span style="
        font-family:'Bricolage Grotesque',sans-serif;
        font-size:3.2rem;font-weight:800;line-height:1;letter-spacing:-0.03em;
        color:{num_col};
      ">{score}</span>
      <span style="font-size:0.7rem;font-weight:500;letter-spacing:0.07em;
                   color:{sub_col};margin-top:0.18rem;">out of 100</span>
    </div>
  </div>
  <div style="
    animation:_fade 0.5s ease 0.7s both;
    display:inline-flex;align-items:center;gap:0.45rem;
    font-family:'Figtree',sans-serif;font-size:0.78rem;font-weight:700;
    letter-spacing:0.08em;text-transform:uppercase;
    padding:0.36rem 1.1rem;border-radius:999px;
    background:{lbl_bg};color:{lbl_col};border:1px solid {lbl_brd};
  ">
    <span style="width:7px;height:7px;border-radius:50%;
                 background:{dot_color};flex-shrink:0;"></span>
    {lbl_text}
  </div>
  <div style="
    display:flex;gap:0.55rem;width:100%;max-width:480px;
    animation:_fade 0.5s ease 0.85s both;
  ">
    {stats_html}
  </div>
</div>
"""

def run_analysis(resume_file, github_url, linkedin_url, job_desc):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name
    resume_file.seek(0)
    try:
        resume_text = extract_and_clean(tmp_path)
    finally:
        os.unlink(tmp_path)
    resume_str = extract_resume_data(api_key, resume_text)
    jd_str = extract_jd_data(api_key, job_desc)
    resume_json = json.loads(resume_str)
    jd_json = json.loads(jd_str)
    match_result = run_matching_pipeline(jd_json, resume_json)
    return transform_result(match_result, resume_json, jd_json, github_url, linkedin_url)

def transform_result(match_result, resume_json, jd_json, github_url, linkedin_url):
    skills_req, skills_pref, skills_miss = [], [], []
    for i, sk in enumerate(match_result.get("skills", [])):
        item = {"id": f"sr{i}", "name": sk["skill"], "evidence": f"Resume: {sk.get('evidence', 'N/A')}"}
        if sk["level"] == "advanced":
            skills_req.append(item)
        elif sk["level"] == "medium":
            skills_pref.append(item)
        else:
            skills_miss.append({"id": f"sx{i}", "name": sk["skill"]})

    experiences = []
    for i, exp in enumerate(resume_json.get("experience", [])):
        lvl = "hi"
        match_items = match_result.get("experience", [])
        if match_items:
            avg = sum(m.get("score", 0) for m in match_items) / len(match_items)
            lvl = "hi" if avg > 0.7 else ("md" if avg > 0.4 else "lo")
        dur = exp.get("duration_years")
        meta = f"{dur} years" if dur else "Duration N/A"
        experiences.append({
            "id": f"ex{i}",
            "name": exp.get("role", "Role N/A"),
            "sub": exp.get("organization", "Organization N/A") or "N/A",
            "meta": meta,
            "level": lvl,
            "evidence": f"Resume: {exp.get('evidence', 'N/A')}",
        })

    educations = []
    for i, edu in enumerate(resume_json.get("education", [])):
        lvl = "hi"
        match_items = match_result.get("education", [])
        if match_items:
            avg = sum(m.get("score", 0) for m in match_items) / len(match_items)
            lvl = "hi" if avg > 0.7 else ("md" if avg > 0.4 else "lo")
        educations.append({
            "id": f"ed{i}",
            "name": f"{edu.get('degree', '')} — {edu.get('field', '') or ''}".strip(" —"),
            "sub": edu.get("institution", "N/A") or "N/A",
            "meta": "",
            "level": lvl,
            "evidence": f"Resume: {edu.get('evidence', 'N/A')}",
        })

    for i, cert in enumerate(resume_json.get("certifications", [])):
        educations.append({
            "id": f"ce{i}",
            "name": cert.get("name", "Certificate"),
            "sub": cert.get("issuer", "N/A") or "N/A",
            "meta": cert.get("year", "") or "",
            "level": "md",
            "evidence": f"Resume: {cert.get('evidence', 'N/A')}",
        })

    risks = []
    if skills_miss:
        risks.append(f"{len(skills_miss)} required skill(s) not evidenced in resume — verification recommended")
    for sk in match_result.get("skills", []):
        if sk["level"] == "low" and sk.get("matched_with"):
            risks.append(f"Skill '{sk['skill']}' has weak evidence — hands-on assessment recommended")
    if not github_url.strip():
        risks.append("GitHub not provided — code skill verification is incomplete")
    if not linkedin_url.strip():
        risks.append("LinkedIn not provided — cross-verification is incomplete")
    for exp_m in match_result.get("experience", []):
        if exp_m.get("level") == "low":
            risks.append(f"Experience match for '{exp_m.get('requirement','')}' is weak — direct verification advised")

    score = match_result.get("final_score", 0)
    return {
        "score": round(score),
        "risks": risks[:5],
        "skills_required": skills_req,
        "skills_preferred": skills_pref,
        "skills_missing": skills_miss,
        "experiences": experiences,
        "educations": educations,
    }

t1, t2 = st.columns([6, 1])
with t2:
    if st.button("☀ Light" if dm else "🌙 Dark", key="dm_btn"):
        st.session_state.dark_mode = not dm
        st.rerun()

st.markdown(f"""
<div class="hero">
  <div class="hero-badge">🔍 Hiring Intelligence &nbsp;·&nbsp; v5.0</div>
  <div class="hero-title">Glass-Box Recruiter</div>
  <div class="hero-sub">Transparent, bias-resistant candidate intelligence</div>
</div>
""", unsafe_allow_html=True)

rk = st.session_state.reset_key
with st.container(border=True):
    st.markdown('<div class="flabel">📄 Resume</div><div class="fhint">PDF · Max 200 MB</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("r", type=["pdf"], key=f"r_{rk}", label_visibility="collapsed")
    if resume_file:
        st.markdown(f'<div class="upload-ok">✔ &nbsp;{resume_file.name} uploaded</div>', unsafe_allow_html=True)

    st.markdown('<div class="gap"></div>', unsafe_allow_html=True)
    st.markdown('<div class="flabel">🔗 GitHub</div><div class="fhint">Optional — improves skill verification</div>', unsafe_allow_html=True)
    github_url = st.text_input("g", placeholder="https://github.com/username", key=f"g_{rk}", label_visibility="collapsed")

    st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)
    st.markdown('<div class="flabel">💼 LinkedIn</div><div class="fhint">Optional — improves experience verification</div>', unsafe_allow_html=True)
    linkedin_url = st.text_input("l", placeholder="https://linkedin.com/in/username", key=f"l_{rk}", label_visibility="collapsed")

    st.markdown('<div class="gap"></div>', unsafe_allow_html=True)
    st.markdown('<div class="flabel">📝 Job Description</div>', unsafe_allow_html=True)
    job_desc = st.text_area("j",
        placeholder="Paste the job description here…\n\nInclude required skills, responsibilities, and specific requirements for accurate evaluation.",
        height=140, key=f"j_{rk}", label_visibility="collapsed")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    ready = bool(resume_file and job_desc.strip())
    st.button("🔍  Analyze Candidate", disabled=not ready, use_container_width=True, key=f"a_{rk}")
    if not ready:
        st.markdown('<div class="hint">Upload a resume and paste a job description to begin</div>', unsafe_allow_html=True)

if st.session_state.get(f"a_{rk}") and ready:
    with st.spinner("Analyzing candidate profile… This may take 15–30 seconds."):
        try:
            st.session_state.result = run_analysis(resume_file, github_url or "", linkedin_url or "", job_desc)
        except ValueError as e:
            st.error(f"⚠️ Configuration Error: {e}")
            st.session_state.result = None
        except Exception as e:
            st.error(f"⚠️ Analysis failed: {e}")
            st.session_state.result = None
    if st.session_state.result:
        st.rerun()

if st.session_state.result:
    r = st.session_state.result
    score, risks = r["score"], r["risks"]
    SKILLS_REQUIRED  = r.get("skills_required", [])
    SKILLS_PREFERRED = r.get("skills_preferred", [])
    SKILLS_MISSING   = r.get("skills_missing", [])
    EXPERIENCES      = r.get("experiences", [])
    EDUCATIONS       = r.get("educations", [])

    with st.container(border=True):
        st.markdown(f"""
        <div class="results-banner">
          <div class="live-dot"></div>
          <div>
            <div class="banner-title">Candidate Analysis Report</div>
            <div class="banner-sub">{len(SKILLS_REQUIRED)+len(SKILLS_PREFERRED)+len(SKILLS_MISSING)+len(EXPERIENCES)+len(EDUCATIONS)} items evaluated &nbsp;·&nbsp; {len(risks)} risk signal{'s' if len(risks)!=1 else ''}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            make_gauge(score, risks_count=len(risks),
                       n_req=len(SKILLS_REQUIRED), n_pref=len(SKILLS_PREFERRED), n_miss=len(SKILLS_MISSING)),
            unsafe_allow_html=True
        )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(sec_head("🧩", "Skills Assessment"), unsafe_allow_html=True)

        req_dot = T['req_text']
        req_brd = "rgba(59,130,246,0.22)" if dm else "rgba(29,78,216,0.15)"
        st.markdown(skill_cat_label(req_dot, req_brd, T['req_text'], "Required"), unsafe_allow_html=True)
        req_html = '<div class="pill-row">'
        for item in SKILLS_REQUIRED:
            req_html += render_skill_pill(item, "req")
        req_html += '</div>'
        for item in SKILLS_REQUIRED:
            req_html += ev_card_html(item["id"], item["evidence"], "req")
        st.markdown(req_html, unsafe_allow_html=True)

        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

        pref_dot = T['pref_text']
        pref_brd = "rgba(124,58,237,0.22)" if dm else "rgba(109,40,217,0.15)"
        st.markdown(skill_cat_label(pref_dot, pref_brd, T['pref_text'], "Preferred"), unsafe_allow_html=True)
        pref_html = '<div class="pill-row">'
        for item in SKILLS_PREFERRED:
            pref_html += render_skill_pill(item, "pref")
        pref_html += '</div>'
        for item in SKILLS_PREFERRED:
            pref_html += ev_card_html(item["id"], item["evidence"], "pref")
        st.markdown(pref_html, unsafe_allow_html=True)

        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

        miss_dot = T['miss_text']
        miss_brd = "rgba(110,140,170,0.15)"
        st.markdown(skill_cat_label(miss_dot, miss_brd, T['miss_text'], "Not Evidenced"), unsafe_allow_html=True)
        miss_html = '<div class="pill-row">'
        for item in SKILLS_MISSING:
            miss_html += render_missing_pill(item)
        miss_html += '</div>'
        st.markdown(miss_html, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(sec_head("💼", "Work Experience"), unsafe_allow_html=True)
        exp_html = ""
        for item in EXPERIENCES:
            exp_html += item_card(item)
            exp_html += ev_card_html(item["id"], item["evidence"], "std")
        st.markdown(exp_html, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(sec_head("🎓", "Education & Certifications"), unsafe_allow_html=True)
        edu_html = ""
        for item in EDUCATIONS:
            edu_html += item_card(item)
            edu_html += ev_card_html(item["id"], item["evidence"], "std")
        st.markdown(edu_html, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(sec_head("⚠️", "Risk Signals"), unsafe_allow_html=True)
        for risk in risks:
            st.markdown(
                f'<div class="risk-item">'
                f'<span class="risk-icon">⚠</span>'
                f'<span class="risk-text">{risk}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("↩  Start New Analysis", use_container_width=True, key="reset"):
            st.session_state.result = None
            st.session_state.reset_key += 1
            st.rerun()

        components.html(ACCORDION_COMPONENT_JS, height=0)

st.markdown(f"""
<div style="text-align:center;margin-top:2.8rem;padding-bottom:1.5rem;">
  <span style="font-size:0.7rem;color:{T['foot']};letter-spacing:0.07em;">
    Glass-Box Recruiter &nbsp;·&nbsp; Ethical AI Hiring &nbsp;·&nbsp; 2025
  </span>
</div>
""", unsafe_allow_html=True)