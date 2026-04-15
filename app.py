import streamlit as st
import json
import os
import httpx
import re
from groq import Groq
from dotenv import load_dotenv

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RoboPath — Robotics & AI Navigator",
    page_icon="🤖",
    layout="centered",
)

load_dotenv()

@st.cache_resource
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please check your .env file.")
        st.stop()
    # Passing an explicit http_client bypasses the 'proxies' argument bug 
    # in the Groq SDK's default initialization.
    return Groq(api_key=api_key, http_client=httpx.Client())

client = get_groq_client()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Header */
.rp-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 2rem;
}
.rp-logo {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -1px;
    color: #111;
}
.rp-logo span { color: #1D9E75; }
.rp-tagline {
    font-size: 13px;
    color: #666;
    margin-top: 2px;
}
.rp-badge {
    margin-left: auto;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    background: #E1F5EE;
    color: #0F6E56;
    border: 1px solid #5DCAA5;
    letter-spacing: 0.04em;
}

/* Step indicator */
.step-row {
    display: flex;
    gap: 8px;
    margin-bottom: 2rem;
}
.step-pill {
    flex: 1;
    text-align: center;
    padding: 8px 4px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    background: #f5f5f5;
    color: #999;
    border: 1px solid #eee;
}
.step-pill.active {
    background: #E1F5EE;
    color: #0F6E56;
    border-color: #5DCAA5;
    font-weight: 600;
}
.step-pill.done {
    background: #1D9E75;
    color: white;
    border-color: #1D9E75;
}

/* Cards */
.info-card {
    background: #f9f9f9;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    color: #111111 !important;
}
.opp-card {
    background: white;
    border: 1.5px solid #e0e0e0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: border-color 0.2s;
}
.opp-card:hover { border-color: #1D9E75; }
.opp-card.selected { border-color: #1D9E75; background: #f0faf6; }

.opp-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.opp-name { font-size: 15px; font-weight: 600; color: #111; }
.opp-badge {
    font-size: 11px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
}
.badge-competition { background: #E1F5EE; color: #0F6E56; }
.badge-internship   { background: #E6F1FB; color: #185FA5; }
.badge-opensource   { background: #FAEEDA; color: #854F0B; }
.opp-desc { font-size: 13px; color: #555; line-height: 1.5; }
.opp-meta { font-size: 11px; color: #888; margin-top: 6px; }

/* Level bar */
.level-bar-outer {
    background: #eee;
    border-radius: 4px;
    height: 8px;
    width: 100%;
    margin: 8px 0;
}
.level-bar-inner {
    height: 8px;
    border-radius: 4px;
    background: #1D9E75;
}

/* Email box */
.email-box {
    background: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #222;
}

/* Chances cards */
.chances-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.chance-card {
    flex: 1;
    min-width: 160px;
    background: #f9f9f9;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #111111 !important;
}
.chance-name { font-size: 13px; font-weight: 600; color: #111111 !important; margin-bottom: 4px; }
.chance-type { font-size: 11px; color: #666666 !important; margin-bottom: 8px; }
.chance-pct { font-family: 'Space Mono', monospace; font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.chance-bar-outer { background: #dddddd; border-radius: 4px; height: 6px; width: 100%; }
.chance-bar-inner { height: 6px; border-radius: 4px; }
.chance-tip { font-size: 11px; color: #555555 !important; margin-top: 6px; line-height: 1.4; }


.metric-row { display: flex; gap: 12px; margin-bottom: 1.5rem; }
.metric-card {
    flex: 1;
    background: #f5f5f5;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    color: #111111 !important;
}
.metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.07em; color: #666666 !important; margin-bottom: 4px; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 20px; font-weight: 700; color: #111111 !important; }

/* Section label */
.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

/* Divider */
.divider { border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "step": 1,
    "profile": {},
    "roadmap_text": "",
    "chances_text": "",
    "opportunities": [],
    "selected_opp_idx": None,
    "email_text": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Load opportunities JSON ───────────────────────────────────────────────────
@st.cache_data
def load_opportunities():
    with open("opportunities.json", "r") as f:
        return json.load(f)

opportunities_db = load_opportunities()

# ── Helper: call Groq ─────────────────────────────────────────────────────────
def call_groq(system_prompt, user_message, max_tokens=900):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rp-header">
  <div>
    <div class="rp-logo">Robo<span>Path</span></div>
    <div class="rp-tagline">Your personalized robotics &amp; AI learning navigator</div>
  </div>
  <div class="rp-badge">AI-Powered</div>
</div>
""", unsafe_allow_html=True)

# ── Step indicator ────────────────────────────────────────────────────────────
step = st.session_state.step
steps = ["01 Profile", "02 Roadmap", "03 Opportunities", "04 Apply"]
pills_html = '<div class="step-row">'
for i, s in enumerate(steps):
    cls = "done" if i + 1 < step else ("active" if i + 1 == step else "step-pill")
    if cls == "done":
        pills_html += f'<div class="step-pill done">✓ {s}</div>'
    else:
        pills_html += f'<div class="step-pill {cls}">{s}</div>'
pills_html += "</div>"
st.markdown(pills_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Profile
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown('<div class="section-label">Tell us about yourself</div>', unsafe_allow_html=True)

    name = st.text_input("Your name")

    grade = st.selectbox("Current grade / year", [
        "Grade 8–9 (Middle school)",
        "Grade 10–11 (High school)",
        "Grade 12 / Pre-university",
        "Undergraduate Year 1–2",
        "Undergraduate Year 3–4",
    ])

    skills = st.multiselect(
        "Tools & skills you already know",
        ["Python", "C++", "Arduino", "ROS", "Raspberry Pi", "Machine Learning",
         "Computer Vision", "3D Printing", "MATLAB", "Electronics basics", "Git/GitHub"],
        placeholder="Select all that apply",
    )

    interest = st.selectbox("Your main interest area", [
        "Humanoid robots", "Autonomous vehicles", "Drone systems",
        "AI & LLMs", "Medical robotics", "Space robotics",
        "Robot manipulation", "Swarm robotics",
    ])

    goal = st.selectbox("Your primary goal", [
        "Get into MIT / top university",
        "Win a robotics competition",
        "Land an internship",
        "Build a project portfolio",
        "Start a robotics startup",
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Academic performance**")
    col_a, col_b = st.columns(2)
    with col_a:
        marks_pct = st.slider("Overall grade / percentage (%)", min_value=40, max_value=100, value=85, step=1)
    with col_b:
        marks_type = st.selectbox("Grading system", ["Percentage (%)", "GPA (out of 4.0)", "CGPA (out of 10)"])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Generate my roadmap →", type="primary", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your name.")
        else:
            st.session_state.profile = {
                "name": name.strip(),
                "grade": grade,
                "skills": skills or ["None yet"],
                "interest": interest,
                "goal": goal,
                "marks": f"{marks_pct} ({marks_type})",
            }
            st.session_state.step = 2
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Roadmap
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    p = st.session_state.profile
    st.markdown('<div class="section-label">Your personalized roadmap</div>', unsafe_allow_html=True)

    if not st.session_state.roadmap_text:
        with st.spinner("AI is mapping your path..."):
            system = (
                "You are RoboPath, a robotics and AI career advisor for students. "
                "Be direct, specific, and encouraging. Use plain text only — no markdown symbols like ** or ##. "
                "Use clear numbered sections."
            )
            prompt = f"""Student profile:
Name: {p['name']}
Grade: {p['grade']}
Academic marks: {p.get('marks', 'Not provided')}
Skills: {', '.join(p['skills'])}
Interest area: {p['interest']}
Goal: {p['goal']}

Give them:
1. Current Level — rate them Beginner / Intermediate / Advanced with a score X/10 and a one-line reason
2. Next 3 Skills to Learn — in order, each with one specific free resource (name + URL)
3. 4-Week Project Idea — one concrete project they can build now
4. Path to Goal — one honest sentence about their specific goal

Keep it concise, specific, and motivating."""
            st.session_state.roadmap_text = call_groq(system, prompt)

    roadmap = st.session_state.roadmap_text

    # Extract level score
    score_match = re.search(r"(\d+)\s*/\s*10", roadmap)
    score = int(score_match.group(1)) if score_match else 6

    # Level label and description
    if score <= 3:
        level_label = "Beginner"
        level_color = "#E24B4A"
        level_desc = "You're just starting out — focus on building fundamentals before jumping into advanced topics."
    elif score <= 6:
        level_label = "Intermediate"
        level_color = "#BA7517"
        level_desc = "You have a solid base. You're ready to take on real projects and start entering competitions."
    elif score <= 8:
        level_label = "Advanced"
        level_color = "#1D9E75"
        level_desc = "Strong profile. Focus on depth, research experience, and standout projects to reach your goal."
    else:
        level_label = "Expert"
        level_color = "#185FA5"
        level_desc = "Exceptional level for a student. You're ready for top-tier internships and university applications."

    # Metric cards
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="metric-label" style="color:#0F6E56">Level score</div>
        <div class="metric-value" style="color:{level_color}">{score}/10 — {level_label}</div>
        <div class="level-bar-outer"><div class="level-bar-inner" style="width:{score*10}%; background:{level_color}"></div></div>
        <div style="font-size:12px; color:#555; margin-top:8px; line-height:1.5">{level_desc}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label" style="color:#185FA5">Interest</div>
        <div class="metric-value" style="font-size:14px; font-family:'DM Sans',sans-serif; margin-top:4px">{p['interest']}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label" style="color:#854F0B">Goal</div>
        <div class="metric-value" style="font-size:13px; font-family:'DM Sans',sans-serif; margin-top:4px">{p['goal']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="info-card" style="white-space:pre-wrap; font-size:14px; line-height:1.75; color:#111111 !important;">{roadmap}</div>', unsafe_allow_html=True)

    # ── Chances Section ──────────────────────────────────────────────────────
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Your admission & competition chances</div>', unsafe_allow_html=True)

    if not st.session_state.chances_text:
        with st.spinner("Calculating your chances..."):
            chances_system = (
                "You are RoboPath. Return ONLY a valid JSON array. No explanation, no markdown, no backticks. "
                "Each object must have: name (string), type (college|competition), "
                "chance (integer 0-100), bar_color (hex color: use #E24B4A for <40, #BA7517 for 40-69, #1D9E75 for 70+), "
                "tip (string, one specific actionable tip to improve chances, max 15 words)."
            )
            chances_prompt = f"""Student profile:
Grade: {p['grade']}
Academic marks: {p.get('marks', 'Not provided')}
Skills: {', '.join(p['skills'])}
Interest: {p['interest']}
Goal: {p['goal']}
Level score: {score}/10

Return a JSON array of 6 entries — 3 colleges/universities and 3 robotics competitions — with realistic admission/acceptance chance percentages for this student RIGHT NOW based on their current profile AND academic marks. Be honest, not overly optimistic."""
            try:
                chances_raw = call_groq(chances_system, chances_prompt, max_tokens=700)
                clean = chances_raw.replace("```json", "").replace("```", "").strip()
                st.session_state.chances_text = clean
            except Exception:
                st.session_state.chances_text = "[]"

    try:
        chances = json.loads(st.session_state.chances_text)
        colleges = [c for c in chances if c.get("type") == "college"]
        competitions = [c for c in chances if c.get("type") == "competition"]

        for section_title, items in [("Universities", colleges), ("Competitions", competitions)]:
            if items:
                st.markdown(f'<div style="font-size:13px; font-weight:600; color:#444; margin:1rem 0 0.5rem">{section_title}</div>', unsafe_allow_html=True)
                cards_html = '<div class="chances-grid">'
                for c in items:
                    pct = c.get("chance", 0)
                    color = c.get("bar_color", "#1D9E75")
                    cards_html += f"""
                    <div class="chance-card">
                        <div class="chance-name">{c.get('name','')}</div>
                        <div class="chance-type">{c.get('type','').capitalize()}</div>
                        <div class="chance-pct" style="color:{color}">{pct}%</div>
                        <div class="chance-bar-outer"><div class="chance-bar-inner" style="width:{pct}%; background:{color}"></div></div>
                        <div class="chance-tip">{c.get('tip','')}</div>
                    </div>"""
                cards_html += "</div>"
                st.markdown(cards_html, unsafe_allow_html=True)
    except Exception:
        st.info("Could not load chances. Try regenerating your roadmap.")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Find opportunities for me →", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.session_state.roadmap_text = ""
            st.session_state.chances_text = ""
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Opportunities
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    p = st.session_state.profile
    st.markdown('<div class="section-label">Opportunities matched to your level</div>', unsafe_allow_html=True)

    if not st.session_state.opportunities:
        with st.spinner("Matching opportunities to your profile..."):
            # Filter from local DB first
            matched = []
            for opp in opportunities_db:
                # Simple matching: by grade range and interest keywords
                grade_ok = p["grade"] in opp.get("grades", []) or "all" in opp.get("grades", [])
                interest_ok = any(
                    kw.lower() in p["interest"].lower() or kw.lower() in " ".join(p["skills"]).lower()
                    for kw in opp.get("keywords", [])
                )
                if grade_ok or interest_ok:
                    matched.append(opp)

            # Fill up to 5 with AI-generated if needed
            if len(matched) < 3:
                system = (
                    "You are RoboPath. Return ONLY a valid JSON array of 3 robotics/AI opportunities. "
                    "No explanation, no markdown. Each object: name, type (competition|internship|opensource), "
                    "description (max 20 words), deadline, why_fit (1 sentence), url."
                )
                prompt = f"Find 3 real opportunities for: Grade: {p['grade']}, Skills: {', '.join(p['skills'])}, Interest: {p['interest']}, Goal: {p['goal']}"
                try:
                    text = call_groq(system, prompt, max_tokens=600)
                    clean = text.replace("```json", "").replace("```", "").strip()
                    ai_opps = json.loads(clean)
                    matched.extend(ai_opps)
                except Exception:
                    pass

            st.session_state.opportunities = matched[:5]

    opps = st.session_state.opportunities
    badge_map = {
        "competition": "badge-competition",
        "internship": "badge-internship",
        "opensource": "badge-opensource",
    }

    selected_idx = st.session_state.selected_opp_idx

    for i, opp in enumerate(opps):
        opp_type = opp.get("type", "competition")
        badge_cls = badge_map.get(opp_type, "badge-competition")
        selected_cls = "selected" if i == selected_idx else ""
        url = opp.get("url", "#")

        st.markdown(f"""
        <div class="opp-card {selected_cls}">
          <div class="opp-header">
            <div class="opp-name">{opp.get('name','')}</div>
            <span class="opp-badge {badge_cls}">{opp_type}</span>
          </div>
          <div class="opp-desc">{opp.get('description','')}</div>
          <div class="opp-meta">{opp.get('deadline','')} · {opp.get('why_fit','')}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Select: {opp.get('name','')}", key=f"sel_{i}", use_container_width=False):
            st.session_state.selected_opp_idx = i
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button(
            "Draft my application →",
            type="primary",
            use_container_width=True,
            disabled=(selected_idx is None),
        ):
            st.session_state.step = 4
            st.session_state.email_text = ""
            st.rerun()
    with col2:
        if st.button("← Back", key="back2", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

    if selected_idx is None:
        st.info("Select one opportunity above to draft your application email.")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Apply
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    p = st.session_state.profile
    opp = st.session_state.opportunities[st.session_state.selected_opp_idx]

    st.markdown('<div class="section-label">AI-drafted outreach email</div>', unsafe_allow_html=True)
    st.markdown(f"Drafting for: **{opp.get('name','')}**")

    if not st.session_state.email_text:
        with st.spinner("Crafting your message..."):
            system = (
                "You are RoboPath. Write a short, genuine, non-generic cold outreach or application email "
                "from a student. It must feel human and specific — no fluff, no excessive compliments. "
                "Plain text only, no markdown. Include a Subject line at the top."
            )
            prompt = f"""Write an outreach email for:
Student: {p['name']}, {p['grade']}
Skills: {', '.join(p['skills'])}
Applying to: {opp.get('name','')} ({opp.get('type','')})
Why relevant: {opp.get('why_fit','')}
Goal: {p['goal']}

Include: Subject line, greeting, 2-3 sentences about who they are and why interested, a specific ask, sign-off.
Keep it under 150 words. Sound like a real ambitious student, not an AI."""
            st.session_state.email_text = call_groq(system, prompt, max_tokens=400)

    email = st.session_state.email_text
    st.markdown(f'<div class="email-box">{email}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.text_area("Edit before sending", value=email, height=220, key="email_edit")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.download_button(
            "Download email (.txt)",
            data=st.session_state.get("email_edit", email),
            file_name="robopath_email.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col2:
        if st.button("← Back", key="back3", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col3:
        if st.button("Start over", use_container_width=True):
            for key in ["step", "profile", "roadmap_text", "chances_text", "opportunities", "selected_opp_idx", "email_text"]:
                del st.session_state[key]
            st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; font-size:13px; color:#888; padding: 0.5rem 0 1.5rem">
        Built with RoboPath · Share your journey on LinkedIn 🚀
    </div>
    """, unsafe_allow_html=True)