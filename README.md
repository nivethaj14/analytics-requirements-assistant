# 📊 Analytics Requirements Assistant

> **Week 1 Project — GenAI Foundations + APIs**
> Transform business requirement documents into structured user stories, acceptance criteria, KPIs, and data model suggestions — powered by **Groq (free & ultra-fast)**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036)
![Free](https://img.shields.io/badge/API-Free-success)

---

## ✨ Features

- **User Stories** — role/goal/benefit format, priority badges, story points
- **Acceptance Criteria** — Given/When/Then format per story
- **KPIs** — targets, descriptions, reporting frequency
- **Data Model** — table schemas with relationships and generated SQL DDL
- **Domain-aware** — pharma, e-commerce, fintech, healthcare, SaaS, marketing, supply chain
- **100% Free** — uses Groq free tier with LLaMA 3.3 70B

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/nivethaj14/analytics-requirements-assistant.git
cd analytics-requirements-assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get your free Groq API key
- Go to [console.groq.com](https://console.groq.com)
- Sign up with Google → Click **API Keys → Create API key**
- Copy the key starting with `gsk_...`

### 5. Run the app
```bash
streamlit run app.py
```

Paste your Groq API key in the sidebar when the app opens.

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, set main file to `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
5. Click **Deploy** 🚀

---

## 🗂️ Project Structure

```
analytics-requirements-assistant/
├── app.py                  # Main Streamlit application (Groq-powered)
├── requirements.txt        # groq + streamlit
├── .streamlit/
│   └── config.toml        # Streamlit theme
├── .gitignore
└── README.md
```

---

## 🧠 Skills Demonstrated

| Skill | How |
|---|---|
| LLM API integration | `groq` Python SDK |
| Prompt engineering | Structured JSON output, system + user roles |
| Streamlit UI | Tabs, expanders, columns, download button |
| Business analysis | User stories, KPIs, data modeling |
| Free tier usage | Groq free tier, LLaMA 3.3 70B |

---

## 📚 Learning Objectives

- [x] LLM fundamentals
- [x] Prompt engineering
- [x] Groq API (OpenAI-compatible)
- [x] Tokens and context windows
- [x] Structured JSON outputs
- [x] Python + Streamlit
- [x] GitHub repository

---

## 📄 License

MIT
