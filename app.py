import streamlit as st
from groq import Groq
import json
import re

st.set_page_config(
    page_title="Analytics Requirements Assistant",
    page_icon="📊",
    layout="wide",
)

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 6px 16px; }
    .story-card {
        background: #f8f9fa; border-radius: 10px;
        padding: 1rem 1.25rem; margin-bottom: 10px;
        border-left: 3px solid #F55036;
    }
    .kpi-card {
        background: #fff4f2; border-radius: 10px;
        padding: 1rem; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Analytics Requirements Assistant")
st.markdown("Transform business requirement documents into structured user stories, acceptance criteria, KPIs, and data model suggestions — powered by **Groq (free & fast)**.")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    import os
api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free key at console.groq.com",
    )
else:
    st.success("✅ API key loaded")
    st.markdown("[🔑 Get free Groq API key](https://console.groq.com)", unsafe_allow_html=False)

    model_choice = st.selectbox(
        "Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        help="70b = best quality · 8b = fastest · mixtral = balanced"
    )

    domain = st.selectbox(
        "Business Domain",
        ["General / Mixed", "Pharma & Life Sciences", "E-commerce & Retail",
         "Finance & Banking", "Healthcare & Clinical", "SaaS / Product Analytics",
         "Marketing & Growth", "Supply Chain & Logistics"],
    )
    st.divider()
    st.markdown("**Week 1 · GenAI Foundations**")
    st.markdown("Skills demonstrated:")
    st.markdown("- 🤖 Groq LLM API integration")
    st.markdown("- 📝 Prompt engineering")
    st.markdown("- 🏗️ Structured JSON outputs")
    st.markdown("- 📊 Business analysis")

# ── Examples ──────────────────────────────────────────────────────────────────
EXAMPLES = {
    "Pharma Commercial KPIs": """We are a mid-sized pharmaceutical company launching two new oncology drugs
across India, Southeast Asia, and the Middle East. Our commercial team needs
an analytics platform to track sales performance, market access, and brand
health across all territories.

The platform must support Regional Business Managers, Medical Science Liaisons,
and the Chief Commercial Officer. Key needs include:

Sales Performance: Track monthly and quarterly net sales by drug, territory,
and sales rep. Monitor prescription (Rx) volumes, new-to-brand prescriptions,
and market share by therapeutic area. Compare actuals vs. forecast and prior
year with variance analysis.

Market Access: Track formulary listings and reimbursement status by country
and payer. Monitor days from approval to first sale (launch readiness).
Flag markets where access is delayed beyond 90 days post-approval.

Field Force Effectiveness: Track HCP (doctor) coverage and call frequency
by rep. Measure samples distributed vs. conversion rate. Monitor territory
alignment and white space opportunities.

Brand Health: Track share of voice vs. competitors. Monitor HCP awareness
and adoption rates across drug lifecycle stages. Measure Net Promoter Score
from HCP surveys quarterly.

Compliance: All data handling must follow 21 CFR Part 11 and local country
pharma marketing regulations. No patient-level data to be stored.

Data sources: SAP (sales), Veeva CRM (field force), IQVIA (market data).""",

    "E-commerce analytics": """We need a sales analytics platform for our e-commerce business.
Marketing and sales teams need to track daily and monthly revenue, customer acquisition costs,
cart abandonment rates, and product-level performance. The system should pull data from our
Shopify store and payment processors. Sales managers want to filter by product category,
date range, and customer segment. We also need automated alerts when conversion rates drop
below 2% or when a product goes out of stock.""",

    "CRM pipeline tracking": """Our sales operations team needs a CRM analytics dashboard to
track the health of our B2B pipeline. We have 12 account executives and need visibility into
deal stages, win/loss rates, average deal size, and sales cycle length. The tool must integrate
with Salesforce and show pipeline velocity by rep and region. Leadership wants a weekly forecast
accuracy metric and flags for deals stuck in a stage for more than 14 days.""",

    "Inventory management": """We run a wholesale distribution business with 3 warehouses.
We need an inventory management system that tracks stock levels in real-time, predicts
stockouts based on historical demand, and auto-generates purchase orders at reorder points.
The operations team needs dashboards for slow-moving inventory, days-on-hand per SKU,
and supplier lead times. Finance wants inventory valuation by location.""",
}

# ── Input ─────────────────────────────────────────────────────────────────────
st.subheader("📄 Requirement Document")

col1, col2 = st.columns([3, 1])
with col2:
    example_choice = st.selectbox("Load example", ["(none)"] + list(EXAMPLES.keys()))

default_text = EXAMPLES.get(example_choice, "") if example_choice != "(none)" else ""
requirement = st.text_area(
    "Paste your business requirement document",
    value=default_text,
    height=220,
    placeholder="Describe the business need, users involved, key metrics, integrations, and constraints...",
)

analyze_btn = st.button("✨ Analyze Requirements", type="primary", use_container_width=True)

# ── Prompt ────────────────────────────────────────────────────────────────────
def build_prompt(req: str, domain_hint: str) -> str:
    return f"""You are a senior business analyst and data architect.
Analyze the following {domain_hint} business requirement document and return ONLY a valid JSON object.
No markdown fences, no explanation, no extra text — raw JSON only.

Use this exact structure:
{{
  "userStories": [
    {{
      "id": "US-001",
      "title": "Short story title",
      "role": "user role",
      "goal": "what they want",
      "benefit": "why they want it",
      "priority": "High|Medium|Low",
      "storyPoints": 3
    }}
  ],
  "acceptanceCriteria": [
    {{
      "storyId": "US-001",
      "criteria": ["Given ... When ... Then ...", "criterion 2"]
    }}
  ],
  "kpis": [
    {{
      "name": "KPI Name",
      "target": "target value",
      "description": "what it measures",
      "frequency": "Daily|Weekly|Monthly"
    }}
  ],
  "dataModel": {{
    "tables": [
      {{
        "name": "table_name",
        "purpose": "what this stores",
        "columns": ["id", "col2", "col3"],
        "relationships": ["references other_table.id"]
      }}
    ],
    "notes": "brief architecture notes"
  }}
}}

Generate 4-6 user stories, acceptance criteria for each, 5-7 KPIs, and 4-6 data model tables.

REQUIREMENT DOCUMENT:
{req}"""

# ── Renderers ─────────────────────────────────────────────────────────────────
def render_stories(stories):
    for s in stories:
        priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(s.get("priority", ""), "⚪")
        st.markdown(f"""
<div class="story-card">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span style="font-size:12px;font-weight:600;color:#F55036">{s.get('id','')}</span>
    <span style="font-size:12px">{priority_icon} {s.get('priority','')} &nbsp;·&nbsp; {s.get('storyPoints','?')} pts</span>
  </div>
  <strong>{s.get('title','')}</strong><br/>
  <span style="font-size:14px;color:#555">
    As a <em>{s.get('role','')}</em>, I want to <em>{s.get('goal','')}</em>,
    so that <em>{s.get('benefit','')}</em>.
  </span>
</div>""", unsafe_allow_html=True)


def render_criteria(criteria, stories):
    story_map = {s["id"]: s["title"] for s in stories}
    for ac in criteria:
        sid = ac.get("storyId", "")
        with st.expander(f"**{sid}** — {story_map.get(sid, '')}", expanded=True):
            for c in ac.get("criteria", []):
                st.markdown(f"✅ {c}")


def render_kpis(kpis):
    cols = st.columns(min(len(kpis), 3))
    for i, k in enumerate(kpis):
        freq_icon = {"Daily": "📅", "Weekly": "📆", "Monthly": "🗓️"}.get(k.get("frequency", ""), "📊")
        with cols[i % 3]:
            st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:13px;color:#666;margin-bottom:4px">{k.get('name','')}</div>
  <div style="font-size:22px;font-weight:600;color:#1a1a2e">{k.get('target','')}</div>
  <div style="font-size:12px;color:#888;margin-top:4px">{k.get('description','')}</div>
  <div style="font-size:12px;margin-top:8px">{freq_icon} {k.get('frequency','')}</div>
</div>""", unsafe_allow_html=True)
            st.write("")


def render_model(model):
    tables = model.get("tables", [])
    if model.get("notes"):
        st.info(f"💡 {model['notes']}")
    for t in tables:
        with st.expander(f"🗃️ `{t.get('name','')}`  — {t.get('purpose','')}", expanded=False):
            cols_str = " · ".join([f"`{c}`" for c in t.get("columns", [])])
            st.markdown(f"**Columns:** {cols_str}")
            for rel in t.get("relationships", []):
                st.markdown(f"🔗 {rel}")

    st.divider()
    st.markdown("**Generated DDL**")
    ddl_lines = []
    for t in tables:
        col_defs = []
        for i, c in enumerate(t.get("columns", [])):
            if i == 0:
                col_defs.append(f"  {c} BIGINT PRIMARY KEY AUTO_INCREMENT")
            elif "_id" in c:
                col_defs.append(f"  {c} BIGINT NOT NULL")
            elif "_at" in c or "date" in c:
                col_defs.append(f"  {c} TIMESTAMP")
            elif any(x in c for x in ["amount", "price", "value", "sales", "revenue"]):
                col_defs.append(f"  {c} DECIMAL(12,2)")
            elif c.startswith("is_") or c.startswith("has_"):
                col_defs.append(f"  {c} BOOLEAN DEFAULT FALSE")
            else:
                col_defs.append(f"  {c} VARCHAR(255)")
        rels = "\n".join([f"  -- {r}" for r in t.get("relationships", [])])
        ddl_lines.append(
            f"CREATE TABLE {t['name']} (\n" + ",\n".join(col_defs) + "\n);"
            + (f"\n{rels}" if rels else "")
        )
    st.code("\n\n".join(ddl_lines), language="sql")


# ── Main ──────────────────────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar. Get one free at console.groq.com")
        st.stop()
    if not requirement.strip():
        st.error("⚠️ Please enter a requirement document.")
        st.stop()

    domain_hint = "" if domain.startswith("General") else f"{domain} domain"

    with st.spinner(f"Analyzing with {model_choice}..."):
        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior business analyst. Always respond with valid raw JSON only. No markdown, no explanation.",
                    },
                    {
                        "role": "user",
                        "content": build_prompt(requirement, domain_hint),
                    },
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content
            clean = re.sub(r"```json|```", "", raw).strip()
            result = json.loads(clean)

        except json.JSONDecodeError:
            st.error("❌ Could not parse the response as JSON. Try again.")
            st.code(raw, language="text")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()

    st.success("✅ Analysis complete!")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["👤 User Stories", "✅ Acceptance Criteria", "📈 KPIs", "🗄️ Data Model"])

    with tab1:
        st.subheader("User Stories")
        stories = result.get("userStories", [])
        total_pts = sum(s.get("storyPoints", 0) for s in stories)
        st.caption(f"{len(stories)} stories · {total_pts} story points total")
        render_stories(stories)

    with tab2:
        st.subheader("Acceptance Criteria")
        render_criteria(result.get("acceptanceCriteria", []), result.get("userStories", []))

    with tab3:
        st.subheader("Key Performance Indicators")
        render_kpis(result.get("kpis", []))

    with tab4:
        st.subheader("Data Model")
        render_model(result.get("dataModel", {}))

    st.divider()
    with st.expander("📋 Raw JSON output"):
        st.json(result)
    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(result, indent=2),
        file_name="requirements_analysis.json",
        mime="application/json",
    )
