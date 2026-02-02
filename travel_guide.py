# travel_guide.py
# ----------------------------------------------------------------
# Travel Guide Generator (Streamlit + OpenAI)
# - Collects travel preferences and constraints
# - Calls GPT models with robust fallbacks
# - Generates day-by-day itinerary
# - Exports clean PDF with 0.5" left/right margins
# ----------------------------------------------------------------

import os
from datetime import datetime
from textwrap import dedent

import streamlit as st  # ✅ REQUIRED
from dotenv import load_dotenv  # ✅ REQUIRED
from openai import OpenAI  # ✅ REQUIRED

# PDF generation (install: pip install reportlab)
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
)

try:
    import streamlit
    import openai
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
except ImportError as e:
    raise SystemExit(
        "\n❌ Missing dependency.\n"
        "Run:\n"
        "  pip install -r requirements.txt\n\n"
        f"Details: {e}\n"
    )
print(f"API Key loaded: {os.getenv('OPENAI_API_KEY')[:10]}..." if os.getenv('OPENAI_API_KEY') else "No API key found!")

# -------------------------
# ENV & CLIENT
# -------------------------
load_dotenv()  # reads .env if present
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# STREAMLIT CONFIG
# -------------------------
st.set_page_config(
    page_title="Travel Guide Generator",
    page_icon="✈️",
    layout="centered",
)

FORM_KEYS = [
    "destination",
    "num_days",
    "special_interests",
    "guardrails",
]

def init_form_state():
    for k in FORM_KEYS:
        st.session_state.setdefault(k, "")
    st.session_state.setdefault("travel_plan", "")

def reset_all_callback():
    """Reset all form fields and clear the generated plan"""
    for k in FORM_KEYS:
        st.session_state[k] = ""
    st.session_state["travel_plan"] = ""
    st.session_state.pop("last_model_used", None)
    st.session_state.pop("last_usage", None)

init_form_state()

st.title("✈️ Travel Guide Generator")
st.caption("Powered by OpenAI & Streamlit")

with st.expander("What this app does", expanded=False):
    st.markdown(
        "- Collects your travel destination and preferences\n"
        "- Generates a **day-by-day itinerary** with places to visit\n"
        "- Considers your special interests and accessibility requirements\n"
        "- Lets you **download a PDF** of your complete travel plan"
    )

# -------------------------
# PROMPTS
# -------------------------
SYSTEM_PROMPT = dedent("""
You are an experienced and enthusiastic TRAVEL GUIDE PLANNER.

Requirements:
- Create a detailed, day-by-day itinerary for the entire trip
- Include specific places, attractions, restaurants, and activities
- Consider the user's special interests and guardrails/constraints
- Provide practical tips like opening hours, estimated time needed, and travel logistics
- Be realistic about timing and distances
- Include local cuisine recommendations where appropriate
- Suggest morning, afternoon, and evening activities for each day

Output format in Markdown with these top-level H2 sections (##):
## Trip Overview
## Day-by-Day Itinerary
(with subsections: ### Day 1, ### Day 2, etc.)
## Travel Tips & Recommendations
## Estimated Budget Overview
## Important Notes & Reminders
""").strip()

def build_user_prompt(destination, num_days, special_interests, guardrails):
    return dedent(f"""
TRAVEL DETAILS
- Destination: {destination or 'N/A'}
- Number of Days: {num_days or 'N/A'}

INTERESTS & PREFERENCES
- Special Interests: {special_interests or 'General sightseeing'}

CONSTRAINTS / GUARDRAILS
{guardrails or 'None specified'}

INSTRUCTIONS
- Create a complete itinerary covering all {num_days} days
- For each day, suggest 3-5 activities/places to visit
- Include specific names of attractions, restaurants, and locations
- Consider travel time between locations
- Incorporate the specified interests throughout the itinerary
- Respect all guardrails and constraints mentioned
- Provide practical details (opening hours, booking requirements, etc.)
- Keep the plan realistic and not overly packed
- Total length: approximately 800-1500 words
""").strip()

# -------------------------
# FALLBACKS & EXTRACTOR
# -------------------------
FALLBACK_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]  # try in order

def _extract_text_from_chat_completion(comp):
    """
    Defensive extractor for minor SDK/shape changes.
    """
    try:
        txt = comp.choices[0].message.content
        if isinstance(txt, str) and txt.strip():
            return txt
        if isinstance(txt, list):
            parts = []
            for p in txt:
                if isinstance(p, str):
                    parts.append(p)
                elif isinstance(p, dict) and isinstance(p.get("text"), str):
                    parts.append(p["text"])
            joined = "\n".join(parts).strip()
            if joined:
                return joined
    except Exception:
        pass
    return ""

def get_travel_plan_markdown(user_prompt):
    """
    Robust call with model fallbacks and modern parameters.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    
    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            comp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2500,
                temperature=0.7,
            )
            text = _extract_text_from_chat_completion(comp)
            if text.strip():
                st.session_state["last_model_used"] = model_name
                st.session_state["last_usage"] = getattr(comp, "usage", None)
                return text
            last_error = RuntimeError(f"Model '{model_name}' returned empty content.")
        except Exception as e:
            last_error = e
            continue
    
    raise RuntimeError(f"All model attempts failed. Last error: {last_error}")

# -------------------------
# PDF HELPERS
# -------------------------
def markdown_to_flowables(md_text, styles):
    """
    Lightweight Markdown -> ReportLab flowables:
    - '## ' -> Heading2
    - '### ' -> Heading3
    - Bullets '-', '*', '•' -> unordered lists
    - Otherwise -> paragraph
    """
    flow = []
    body = styles["BodyText"]
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], spaceBefore=8, spaceAfter=4)
    
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        if not line.strip():
            flow.append(Spacer(1, 6))
            i += 1
            continue
        
        if line.startswith("## "):
            flow.append(Paragraph(line[3:].strip(), h2))
            i += 1
            continue
        if line.startswith("### "):
            flow.append(Paragraph(line[4:].strip(), h3))
            i += 1
            continue
        
        if line.lstrip().startswith(("-", "*", "•")):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith(("-", "*", "•")):
                bullet_text = lines[i].lstrip()[1:].strip()
                items.append(ListItem(Paragraph(bullet_text, body), leftIndent=12))
                i += 1
            flow.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=6))
            flow.append(Spacer(1, 4))
            continue
        
        flow.append(Paragraph(line, body))
        i += 1
    
    return flow

def write_pdf(markdown_text, destination, filename="travel_plan.pdf"):
    # Letter with 0.5" left/right margins (and ~0.7" top/bottom)
    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=f"Travel Guide - {destination}",
        author="Travel Guide Generator",
    )
    styles = getSampleStyleSheet()
    
    header = ParagraphStyle(
        "Header",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=12,
    )
    
    story = []
    story.append(Paragraph(f"Travel Guide: {destination}", header))
    meta = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    story.append(Paragraph(meta, styles["Normal"]))
    story.append(Spacer(1, 10))
    
    story.extend(markdown_to_flowables(markdown_text, styles))
    doc.build(story)
    return filename

# -------------------------
# INPUT FORM
# -------------------------
with st.form("travel_inputs"):
    st.text_input(
        "1) Destination to Travel",
        placeholder="e.g., Paris, France or Tokyo, Japan",
        key="destination"
    )
    
    st.text_input(
        "2) Number of Days",
        placeholder="e.g., 5 or 7 days",
        key="num_days"
    )
    
    st.text_area(
        "3) Special Interests",
        placeholder="e.g., Museums, Food & Cuisine, Historic sites, Nightlife, Nature, Shopping, Photography",
        key="special_interests",
        height=100
    )
    
    st.text_area(
        "4) Guardrails / Constraints",
        placeholder="e.g., No walking tours, only kids friendly activities, wheelchair accessible places only, budget-friendly options",
        key="guardrails",
        height=100
    )
    
    submitted = st.form_submit_button("🗺️ Generate Travel Plan")

# -------------------------
# QUICK API SELF-TEST
# -------------------------
with st.expander("Diagnostics (optional)", expanded=False):
    if st.button("Run quick API self-test"):
        try:
            ping = client.chat.completions.create(
                model=FALLBACK_MODELS[0],
                messages=[{"role": "user", "content": "Reply with the single word: READY"}],
                max_tokens=10,
            )
            st.success("Self-test response:")
            st.code(_extract_text_from_chat_completion(ping))
        except Exception as e:
            st.error(f"Self-test failed: {e}")

# -------------------------
# MAIN ACTION
# -------------------------
if submitted:
    if not (st.session_state["destination"] and st.session_state["num_days"]):
        st.warning("Please provide at least **Destination** and **Number of Days**.")
    else:
        with st.spinner("Creating your personalized travel plan..."):
            user_prompt = build_user_prompt(
                st.session_state["destination"],
                st.session_state["num_days"],
                st.session_state["special_interests"],
                st.session_state["guardrails"],
            )
            st.session_state["travel_plan"] = get_travel_plan_markdown(user_prompt)
        
        if st.session_state["travel_plan"].strip():
            st.success("✅ Travel plan generated!")
            st.caption(f"Model: {st.session_state.get('last_model_used', 'unknown')}")
            if st.session_state.get("last_usage"):
                st.caption(f"Usage: {st.session_state['last_usage']}")
            
            st.subheader(f"Your Travel Plan for {st.session_state['destination']}")
            st.markdown(st.session_state["travel_plan"], unsafe_allow_html=False)
            
            with st.expander("Show raw text (copy-friendly)"):
                st.text_area("Plan (raw)", st.session_state["travel_plan"], height=400)
            
            # PDF export
            try:
                pdf_path = write_pdf(
                    st.session_state["travel_plan"],
                    st.session_state["destination"],
                    filename="travel_plan.pdf"
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Travel Plan PDF",
                        data=f.read(),
                        file_name=f"travel_guide_{st.session_state['destination'].replace(' ', '_').replace(',', '')}.pdf",
                        mime="application/pdf",
                    )
            except Exception as e:
                st.error(f"PDF generation error: {e}")
                st.info("You can still copy the plan above while we sort out PDF export.")
        else:
            st.warning("The model returned an empty response.")
            st.info("Try again, or verify your API key/model access in Diagnostics above.")
else:
    if "travel_plan" in st.session_state and st.session_state["travel_plan"].strip():
        st.subheader("Last Generated Travel Plan")
        st.markdown(st.session_state["travel_plan"], unsafe_allow_html=False)
    else:
        st.info("Fill in the fields above and click **Generate Travel Plan**.")

st.divider()

# Reset button (centered)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.button(
        "🔄 Reset Form",
        type="primary",
        on_click=reset_all_callback,
        use_container_width=True
    )
