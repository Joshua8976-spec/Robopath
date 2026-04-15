# 🤖 RoboPath — Personalized Robotics & AI Learning Navigator

RoboPath is a free AI-powered tool for students who want to break into robotics and AI.

It maps your current skills, builds a personalized learning roadmap, surfaces real competitions and internships matched to your level, and drafts your outreach email — all in one flow.

---

## Features

- **Profile builder** — Grade, skills, interest area, and goal
- **AI Roadmap** — Level score, next 3 skills to learn, 4-week project idea
- **Opportunity matcher** — Competitions, internships, and open-source programs from a curated database + AI
- **Email drafter** — Genuine, specific outreach email you can send immediately
- **Download** — Save your email as a .txt file

---

## Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [Groq API](https://groq.com) — LLM inference (llama-3.3-70b-versatile)
- Python 3.10+

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/robopath.git
cd robopath
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key
```bash
cp .env.example .env
# Edit .env and paste your Groq API key
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run locally
```bash
streamlit run app.py
```

---

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Add `GROQ_API_KEY` in the **Secrets** section (Settings → Secrets)
5. Deploy!

---

## Project Structure

```
robopath/
├── app.py                # Main Streamlit app
├── opportunities.json    # Curated robotics opportunities database
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Built by

Joshua — a student on a mission to get into MIT for robotics and AI.  
Part of a 19-project AI portfolio.

---

## License

MIT
