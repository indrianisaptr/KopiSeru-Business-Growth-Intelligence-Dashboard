"""
components/ai_analyst.py
AI Business Development Copilot - Reusable component for all dashboard pages.
Powered by Groq API (LLaMA 3.3 70B).
"""

import streamlit as st
import json
from utils.data_loader import COLORS


def _get_groq_client():
    """Get Groq client with API key from secrets."""
    try:
        from groq import Groq
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except Exception:
        return None


def _build_system_prompt() -> str:
    """System prompt for AI analyst."""
    return """You are an expert Business Intelligence Analyst for KopiSeru, 
a growing Indonesian coffee shop chain. Your role is to help the Business 
Development Manager make data-driven decisions.

STRICT RULES:
1. Only answer based on the data and context provided.
2. Always be concise but insightful.
3. Provide actionable business recommendations.
4. Use Indonesian business context when relevant.
5. When providing insight, keep it to 2-3 sentences max.
6. Numbers should reference the actual data provided in the context.

You understand the following KopiSeru business context:
- KopiSeru is a fictional Indonesian coffee chain operating since 2018
- It has 40 branches across 9 cities
- Data covers 2021-2023 operational period
- Key metrics: revenue, profit, transactions, customer satisfaction, channel distribution
- Branch types: Mall (highest margin ~35%), Office Area, Stand Alone, University (negative margin)
- Top expansion candidates: Makassar and Denpasar based on profitability + low saturation
- Promotions boost volume but not necessarily profit margin
- Weekend shows ~19% lower profit despite similar revenue to weekdays
- Customer satisfaction averages 3.84/5, mainly influenced by branch type (not weather/promo)
- Delivery channel is growing year-over-year consistently
"""


def _build_context_prompt(filters: dict, stats: dict, page_name: str) -> str:
    """Build data context for efficient token usage."""
    filter_str = json.dumps(
        {k: v for k, v in filters.items() if v},
        ensure_ascii=False, indent=2
    )
    stats_str = (
        f"Total Revenue: Rp {stats.get('total_revenue', 0):,.0f}\n"
        f"Total Profit: Rp {stats.get('total_profit', 0):,.0f}\n"
        f"Avg Profit Margin: {stats.get('avg_profit_margin', 0):.1f}%\n"
        f"Total Transactions: {stats.get('total_transactions', 0):,.0f}\n"
        f"Avg Ticket Size: Rp {stats.get('avg_ticket_size', 0):,.0f}\n"
        f"Avg Customer Satisfaction: {stats.get('avg_satisfaction', 0):.2f}/5\n"
        f"Active Branches: {stats.get('num_branches', 0)}\n"
        f"Cities Covered: {stats.get('num_cities', 0)}\n"
        f"Data Records: {stats.get('rows', 0):,}"
    )
    return f"""
=== CURRENT DASHBOARD CONTEXT ===
Page: {page_name}

Active Filters:
{filter_str}

Current Data Summary (filtered):
{stats_str}
=== END CONTEXT ===
"""


def _summarize_df(df, max_rows: int = 12) -> str:
    """Compact text preview of a chart's underlying (already-filtered) data."""
    try:
        return df.head(max_rows).to_string(index=False)
    except Exception:
        return str(df)


def explain_chart(
    chart_title: str,
    chart_df,
    filters: dict,
    stats: dict,
    page_name: str,
    max_tokens: int = 500,
) -> str:
    """
    Reusable "Explain This Chart" function. Sends the chart title plus a
    preview of the currently filtered data behind that chart to Groq, and
    asks for: what the chart shows, key insight, business interpretation,
    and what the Business Development Manager should watch out for.
    """
    client = _get_groq_client()
    if client is None:
        return (
            "AI Analyst is unavailable. Please add your GROQ_API_KEY to "
            "`.streamlit/secrets.toml` to enable this feature."
        )

    context = _build_context_prompt(filters, stats, page_name)
    data_preview = _summarize_df(chart_df)

    prompt = f"""{context}

Chart being viewed: "{chart_title}"

Underlying data behind this chart (already filtered, preview rows):
{data_preview}

Explain this chart to a Business Development Manager. Structure your answer with:
1. Apa yang ditampilkan chart ini.
2. Insight utama dari data yang sedang aktif.
3. Interpretasi bisnis dari insight tersebut.
4. Hal yang perlu diperhatikan Business Development Manager.

Keep it concise and reference the actual numbers shown above."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI request failed: {str(e)}"


def render_chart_explainer(
    chart_title: str,
    chart_df,
    filters: dict,
    stats: dict,
    page_name: str,
    key: str,
) -> None:
    """
    Reusable "Explain This Chart" button + answer, meant to be placed
    directly below any st.plotly_chart() call on any page. Single shared
    implementation so every chart on every page behaves identically.
    """
    from components.metrics import ai_insight_card

    if st.button("🔍 Explain This Chart", key=f"explain_{page_name}_{key}"):
        with st.spinner("Analyzing chart..."):
            explanation = explain_chart(chart_title, chart_df, filters, stats, page_name)
        ai_insight_card(explanation.replace("\n", "<br>"))



def ask_ai(
    question: str,
    filters: dict,
    stats: dict,
    page_name: str,
    max_tokens: int = 600,
) -> str:
    """
    Send a question to Groq and return the response text.
    Returns an error message string if the call fails.
    """
    client = _get_groq_client()
    if client is None:
        return (
            "AI Analyst is unavailable. Please add your GROQ_API_KEY to "
            "`.streamlit/secrets.toml` to enable this feature."
        )

    context = _build_context_prompt(filters, stats, page_name)
    full_question = f"{context}\n\nUser Question: {question}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": full_question},
            ],
            temperature=0.4,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI request failed: {str(e)}"


def generate_page_insight(filters: dict, stats: dict, page_name: str) -> str:
    """Generate a brief AI insight card for the current page."""
    prompt = (
        f"Based on the current data for the '{page_name}' page, "
        "provide ONE key actionable insight in 2-3 sentences for the "
        "Business Development Manager. Be specific about numbers from the data."
    )
    return ask_ai(prompt, filters, stats, page_name, max_tokens=200)


def render_business_copilot(
    filters: dict,
    stats: dict,
    page_name: str,
    suggested_questions: list[str],
) -> None:
    """
    Render Business Development Copilot section at the bottom of each page.
    
    Args:
        filters: Active sidebar filters
        stats: Summary statistics from current filtered data
        page_name: Current page name (for AI context)
        suggested_questions: List of 3-4 pre-written questions specific to the page
    """
    from components.metrics import ai_insight_card

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background:{COLORS['bg']}; border:2px solid {COLORS['accent']};
                    border-radius:12px; padding:20px; margin:20px 0;
                    font-size:13px; color:{COLORS['text_muted']};">
            <div style="font-weight:700; color:{COLORS['primary']}; margin-bottom:8px;">
                Business Development Copilot
            </div>
            This AI assistant has access to the current filtered data and KopiSeru 
            business context. Ask anything about the data or get strategic recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tab 1: AI Executive Insight ───────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["AI Insight", "Ask AI", "Recommended Actions"])

    with tab1:
        st.subheader("AI Executive Insight")
        if st.button("Generate Insight", key=f"ai_insight_{page_name}"):
            with st.spinner("Analyzing data..."):
                insight = generate_page_insight(filters, stats, page_name)
            ai_insight_card(insight.replace("\n", "<br>"))

    # ── Tab 2: Suggested Questions + Free-form Ask ────────────────────────
    with tab2:
        st.subheader("Suggested Questions")
        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            col = cols[i % 2]
            with col:
                if st.button(question, key=f"suggested_{page_name}_{i}",
                           use_container_width=True):
                    st.session_state[f"ai_question_{page_name}"] = question
                    with st.spinner("Analyzing..."):
                        st.session_state[f"ai_answer_{page_name}"] = ask_ai(
                            question, filters, stats, page_name, max_tokens=800
                        )

        st.markdown("---")
        st.subheader("Ask Your Own Question")
        user_q = st.text_area(
            "Your question:",
            value=st.session_state.get(f"ai_question_{page_name}", ""),
            height=80,
            placeholder="e.g. Mengapa profit weekend lebih rendah? Cabang mana yang perlu fokus?",
            key=f"custom_question_{page_name}",
        )

        if st.button("Ask AI", type="primary", use_container_width=True,
                    key=f"ask_btn_{page_name}"):
            if user_q.strip():
                with st.spinner("Analyzing..."):
                    st.session_state[f"ai_answer_{page_name}"] = ask_ai(
                        user_q, filters, stats, page_name, max_tokens=800
                    )

        if st.session_state.get(f"ai_answer_{page_name}"):
            ai_insight_card(st.session_state[f"ai_answer_{page_name}"].replace("\n", "<br>"))

    # ── Tab 3: Action Recommendations ────────────────────────────────────
    with tab3:
        st.subheader("Recommended Actions")
        if st.button("Generate Recommendations", key=f"recommendations_{page_name}"):
            with st.spinner("Generating recommendations..."):
                rec_prompt = (
                    f"For the '{page_name}' page with current data, provide 3-4 specific, "
                    "actionable business recommendations that the Business Development Manager "
                    "should prioritize. Format each as a numbered item with action + rationale."
                )
                recommendations = ask_ai(
                    rec_prompt, filters, stats, page_name, max_tokens=600
                )
            ai_insight_card(recommendations.replace("\n", "<br>"))