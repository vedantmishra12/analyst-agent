"""AI Data Analyst — Main Streamlit Application."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd

from config.settings import THEME, SUPPORTED_MODELS, OLLAMA_HOST
from database.db_service import DatabaseService
from services.ollama_service import OllamaService
from services.profiler_service import ProfilerService
from agents.analyst_agent import AnalystAgent
from charts.chart_service import ChartService
from reports.report_service import ReportService
from utils.ui_helpers import (
    inject_css, kpi_card, section_header, file_badge, table_badge,
    chat_bubble_user, chat_bubble_ai, sql_block, info_box, warn_box,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Session State Init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "db":           DatabaseService(),
        "ollama":       OllamaService(OLLAMA_HOST),
        "profiler":     ProfilerService(),
        "agent":        None,
        "charts":       ChartService(),
        "reporter":     ReportService(),
        "chat_history": [],
        "sql_history":  [],
        "profiles":     {},
        "model":        "llama3",
        "ollama_models":[],
        "files_loaded": False,
        "exec_summary": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

db       = st.session_state["db"]
ollama   = st.session_state["ollama"]
profiler = st.session_state["profiler"]
charts   = st.session_state["charts"]
reporter = st.session_state["reporter"]

# Rebuild agent whenever model changes
def get_agent() -> AnalystAgent:
    return AnalystAgent(ollama, db)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:8px 0 20px'>
        <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;
             background:linear-gradient(135deg,{THEME["accent"]},{THEME["accent2"]});
             -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
            AI DATA ANALYST
        </div>
        <div style='font-size:.65rem;color:{THEME["muted"]};letter-spacing:2px;margin-top:2px'>
            POWERED BY OLLAMA + DUCKDB
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Ollama Status ────────────────────────────────────────────────────────
    section_header("Model", "🤖")
    is_up = ollama.is_running()
    status_color = THEME["accent3"] if is_up else THEME["danger"]
    status_text  = "● Online" if is_up else "● Offline"
    st.markdown(f"<span style='color:{status_color};font-size:.8rem;font-weight:700'>{status_text} — Ollama</span>", unsafe_allow_html=True)

    if not is_up:
        warn_box("Ollama not running.<br>Run: <code>ollama serve</code> in Terminal")

    if st.button("🔍 Detect Models", use_container_width=True):
        found = ollama.list_models()
        st.session_state["ollama_models"] = found if found else SUPPORTED_MODELS
        if found:
            st.success(f"Found {len(found)} model(s)")
        else:
            st.warning("No models found. Using defaults.")

    model_list = st.session_state["ollama_models"] or SUPPORTED_MODELS
    selected_model = st.selectbox("Active Model", model_list, label_visibility="collapsed")
    st.session_state["model"] = selected_model
    st.markdown(f"<div class='ai-badge' style='margin:4px 0'>🦙 {selected_model}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── File Upload ──────────────────────────────────────────────────────────
    section_header("Data", "📂")
    uploads = st.file_uploader(
        "Upload files",
        type=["csv", "xlsx", "xls", "parquet"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploads:
        for f in uploads:
            if f.name not in [t.get("file","") for t in db.tables.values()]:
                with st.spinner(f"Loading {f.name}…"):
                    try:
                        table = db.register_file(f.getvalue(), f.name)
                        meta  = db.tables[table]
                        prof  = profiler.profile(meta["df"], table)
                        st.session_state["profiles"][table] = prof
                        st.session_state["files_loaded"] = True
                        st.success(f"✅ {f.name} → `{table}`")
                    except Exception as e:
                        st.error(f"❌ {f.name}: {e}")

    if db.tables:
        st.markdown("**Tables loaded:**")
        for name in db.get_table_names():
            meta = db.tables[name]
            st.markdown(table_badge(f"{name} · {meta['rows']:,}r"), unsafe_allow_html=True)

        if st.button("🗑️ Clear All Data", use_container_width=True):
            db.clear()
            st.session_state["profiles"]     = {}
            st.session_state["chat_history"] = []
            st.session_state["sql_history"]  = []
            st.session_state["exec_summary"] = {}
            st.session_state["files_loaded"] = False
            st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:.7rem;color:{THEME["muted"]};line-height:1.8'>
        <b style='color:{THEME["text"]}'>Quick Start</b><br>
        1. Run <code>ollama serve</code><br>
        2. Pull a model: <code>ollama pull llama3</code><br>
        3. Upload a CSV/Excel/Parquet<br>
        4. Ask questions in Chat tab
    </div>
    """, unsafe_allow_html=True)

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding:4px 0 20px'>
    <h1 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;margin:0;
        background:linear-gradient(135deg,{THEME["accent"]},{THEME["accent2"]});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        AI Data Analyst
    </h1>
    <p style='color:{THEME["muted"]};font-size:.78rem;letter-spacing:2px;margin:4px 0 0'>
        SENIOR ANALYST · DUCKDB · OLLAMA · LOCAL AI
    </p>
</div>
""", unsafe_allow_html=True)

# No files — landing screen
if not st.session_state["files_loaded"]:
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Files Supported", "CSV · XLS · Parquet", THEME["accent"])
    kpi_card(c2, "AI Engine",  "Ollama (Local)", THEME["accent2"])
    kpi_card(c3, "Analytics",  "DuckDB + Polars", THEME["accent3"])
    kpi_card(c4, "Privacy",    "100% Local", THEME["warn"])

    st.markdown(f"""
    <div style='text-align:center;padding:60px 20px;color:{THEME["muted"]}'>
        <div style='font-size:3.5rem;margin-bottom:16px'>📊</div>
        <div style='font-size:1.1rem;color:{THEME["text"]};font-weight:600;margin-bottom:8px'>
            Upload your data to get started
        </div>
        <div style='font-size:.85rem;max-width:480px;margin:0 auto;line-height:1.7'>
            Upload CSV, Excel, or Parquet files in the sidebar.<br>
            The AI will automatically profile your data and you can start asking questions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_chat, tab_profile, tab_schema, tab_dashboard, tab_report = st.tabs([
    "💬 Chat Analyst",
    "🔬 Data Profile",
    "🗄️ Schema Explorer",
    "📈 Dashboard",
    "📄 Report",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT ANALYST
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    col_chat, col_info = st.columns([3, 1])

    with col_info:
        section_header("Quick Questions", "💡")
        sample_qs = [
            "Show top 10 rows",
            "What is the row count?",
            "Show column statistics",
            "Find duplicate records",
            "Show missing value summary",
            "What are the top 5 categories?",
            "Show revenue by month",
            "Which segment has highest sales?",
        ]
        for q in sample_qs:
            if st.button(q, key=f"sq_{q}", use_container_width=True):
                st.session_state["pending_q"] = q

        st.markdown("---")
        section_header("Tables", "⬡")
        for name, meta in db.tables.items():
            with st.expander(f"{name}"):
                for col in meta["cols"]:
                    st.markdown("<span style='font-size:.72rem;font-family:monospace;color:" + THEME["muted"] + "'>" + col["name"] + " <span style='color:" + THEME["accent3"] + "'>" + col["dtype"] + "</span></span>", unsafe_allow_html=True)

    with col_chat:
        section_header("Data Analyst Chat", "💬")
        st.markdown("<div style='font-size:.78rem;color:" + THEME["muted"] + ";margin-bottom:16px'>Ask any business question. The AI generates SQL, executes it, and explains findings.</div>", unsafe_allow_html=True)

        # Chat history display
        chat_container = st.container()
        with chat_container:
            for turn in st.session_state["chat_history"]:
                chat_bubble_user(turn["q"])
                if turn.get("sql"):
                    sql_block(turn["sql"])
                if turn.get("results") is not None and not turn["results"].empty:
                    with st.expander(f"📊 Results — {len(turn['results'])} rows", expanded=False):
                        st.dataframe(turn["results"].head(100), use_container_width=True)
                chat_bubble_ai(turn.get("analysis", ""))
                if turn.get("chart"):
                    st.plotly_chart(turn["chart"], use_container_width=True)
                st.markdown("---")

        # Input
        user_input = st.chat_input("Ask a business question about your data…")
        pending    = st.session_state.pop("pending_q", None)
        question   = user_input or pending

        if question:
            if not is_up:
                st.error("❌ Ollama is not running. Start it with: `ollama serve`")
            else:
                agent = get_agent()
                model = st.session_state["model"]

                with st.spinner("🤔 Generating SQL…"):
                    sql = agent.generate_sql(question, model)

                result_df = pd.DataFrame()
                error_msg = None

                if sql:
                    with st.spinner("⚡ Executing query…"):
                        result_df, error_msg = db.execute(sql)

                analysis = ""
                with st.spinner("🧠 Analysing results…"):
                    if error_msg:
                        analysis = f"⚠️ SQL Error: {error_msg}\n\nLet me try a different approach. {agent.generate_sql(question + ' (simpler query)', model)}"
                    elif result_df is not None:
                        analysis = agent.analyze_results(question, sql, result_df, model)
                    else:
                        analysis = "No results returned."

                # Chart
                chart_fig = None
                if result_df is not None and not result_df.empty and len(result_df) > 1:
                    with st.spinner("📈 Building chart…"):
                        chart_cfg = agent.suggest_chart(question, result_df, model)
                        chart_fig = charts.build(result_df, chart_cfg)

                turn = {
                    "q":        question,
                    "sql":      sql,
                    "results":  result_df if result_df is not None else pd.DataFrame(),
                    "analysis": analysis,
                    "chart":    chart_fig,
                }
                st.session_state["chat_history"].append(turn)
                st.session_state["sql_history"].append({
                    "question": question,
                    "sql":      sql,
                    "analysis": analysis,
                })
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_profile:
    if not st.session_state["profiles"]:
        info_box("Upload data to see profiling results.")
    else:
        table_names = list(st.session_state["profiles"].keys())
        sel_table   = st.selectbox("Select table:", table_names) if len(table_names) > 1 else table_names[0]
        prof        = st.session_state["profiles"][sel_table]

        # KPI row
        c1, c2, c3, c4, c5 = st.columns(5)
        kpi_card(c1, "Total Rows",    f"{prof['rows']:,}",             THEME["accent"])
        kpi_card(c2, "Columns",       prof["cols"],                    THEME["accent2"])
        kpi_card(c3, "Completeness",  f"{prof['completeness']}%",      THEME["accent3"])
        kpi_card(c4, "Duplicates",    f"{prof['duplicates']:,}",       THEME["danger"] if prof["duplicates"] else THEME["accent3"])
        kpi_card(c5, "Missing Vals",  f"{prof['missing_total']:,}",    THEME["warn"] if prof["missing_total"] else THEME["accent3"])

        st.markdown("")

        col_l, col_r = st.columns([2, 1])

        with col_l:
            section_header("Column Details", "📋")
            for cp in prof["col_profiles"]:
                icon = "🔢" if "mean" in cp else "🔤"
                with st.expander(f"{icon} {cp['name']} · {cp['dtype']} · {cp['null_pct']}% missing"):
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Unique",   cp["unique"])
                    m2.metric("Missing",  f"{cp['null_pct']}%")
                    m3.metric("Non-null", prof["rows"] - cp["nulls"])
                    if "mean" in cp:
                        s1, s2, s3, s4 = st.columns(4)
                        s1.metric("Mean",     cp["mean"])
                        s2.metric("Std",      cp.get("std", "—"))
                        s3.metric("Min",      cp["min"])
                        s4.metric("Max",      cp["max"])
                        if cp.get("outliers", 0) > 0:
                            warn_box(f"{cp['outliers']} outlier(s) detected (IQR method)")
                    if "top_values" in cp:
                        st.markdown("**Top values:**")
                        tv_df = pd.DataFrame(cp["top_values"])
                        st.dataframe(tv_df, use_container_width=True, hide_index=True)

        with col_r:
            section_header("AI Executive Summary", "🤖")
            if not is_up:
                warn_box("Ollama offline — start it to get AI summary.")
            else:
                if sel_table not in st.session_state["exec_summary"]:
                    if st.button("✨ Generate Summary", use_container_width=True):
                        prof_text = profiler.profile_to_text(prof)
                        with st.spinner("Generating executive summary…"):
                            summary = get_agent().generate_executive_summary(
                                prof_text, st.session_state["model"]
                            )
                        st.session_state["exec_summary"][sel_table] = summary

                if sel_table in st.session_state["exec_summary"]:
                    st.markdown(st.session_state["exec_summary"][sel_table])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SCHEMA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_schema:
    section_header("Database Schema", "🗄️")

    if not db.tables:
        info_box("No tables loaded. Upload data first.")
    else:
        for table_name, meta in db.tables.items():
            with st.expander(f"⬡ {table_name}  ·  {meta['rows']:,} rows  ·  {meta['columns']} columns  ·  📄 {meta['file']}", expanded=True):
                cols_data = pd.DataFrame(meta["cols"])
                st.dataframe(
                    cols_data[["name", "dtype", "nulls", "null_pct", "unique"]].rename(columns={
                        "name": "Column", "dtype": "Type", "nulls": "Null Count",
                        "null_pct": "Null %", "unique": "Unique Values"
                    }),
                    use_container_width=True, hide_index=True
                )

                st.markdown(f"**Sample Data** (first 10 rows):")
                sample_sql = f"SELECT * FROM {table_name} LIMIT 10"
                sample_df, _ = db.execute(sample_sql)
                if sample_df is not None:
                    st.dataframe(sample_df, use_container_width=True)

        st.markdown("---")
        section_header("SQL Playground", "⚡")
        st.markdown("<div style='font-size:.78rem;color:" + THEME["muted"] + ";margin-bottom:8px'>Write and execute read-only SQL against your data.</div>", unsafe_allow_html=True)

        user_sql = st.text_area(
            "SQL Query",
            value=f"SELECT * FROM {list(db.tables.keys())[0]} LIMIT 20" if db.tables else "SELECT 1",
            height=120,
            label_visibility="collapsed",
        )
        if st.button("▶ Run Query", use_container_width=False):
            result, err = db.execute(user_sql)
            if err:
                st.error(f"SQL Error: {err}")
            elif result is not None:
                st.success(f"✅ {len(result)} rows returned")
                st.dataframe(result, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dashboard:
    section_header("Auto Dashboard", "📈")

    if not db.tables:
        info_box("Upload data to generate dashboard.")
    else:
        table_names = list(db.tables.keys())
        dash_table  = st.selectbox("Dashboard source:", table_names, key="dash_sel") if len(table_names) > 1 else table_names[0]
        prof        = st.session_state["profiles"].get(dash_table, {})
        meta        = db.tables[dash_table]

        # KPI row
        c1, c2, c3, c4 = st.columns(4)
        kpi_card(c1, "Total Records",  f"{meta['rows']:,}",        THEME["accent"])
        kpi_card(c2, "Columns",        meta["columns"],             THEME["accent2"])
        kpi_card(c3, "Completeness",   f"{prof.get('completeness','—')}%", THEME["accent3"])
        kpi_card(c4, "Duplicates",     f"{prof.get('duplicates', 0):,}", THEME["warn"])

        st.markdown("")

        numeric_cols = prof.get("numeric_cols", [])
        cat_cols     = prof.get("cat_cols", [])

        if numeric_cols and cat_cols:
            col_l, col_r = st.columns(2)

            # Bar chart: top categorical by first numeric
            cat_col = cat_cols[0]
            num_col = numeric_cols[0]
            bar_sql = f"""
                SELECT {cat_col}, SUM("{num_col}") AS total_{num_col}
                FROM {dash_table}
                WHERE {cat_col} IS NOT NULL
                GROUP BY {cat_col}
                ORDER BY total_{num_col} DESC
                LIMIT 15
            """
            bar_df, _ = db.execute(bar_sql)
            with col_l:
                if bar_df is not None and not bar_df.empty:
                    fig = charts.quick_bar(bar_df, cat_col, f"total_{num_col}",
                                           f"Top {cat_col} by {num_col}")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

            # Pie if second cat exists
            with col_r:
                if len(cat_cols) > 1:
                    cat2 = cat_cols[1]
                    pie_sql = f"""
                        SELECT {cat2}, COUNT(*) AS count
                        FROM {dash_table}
                        WHERE {cat2} IS NOT NULL
                        GROUP BY {cat2}
                        ORDER BY count DESC
                        LIMIT 8
                    """
                    pie_df, _ = db.execute(pie_sql)
                    if pie_df is not None and not pie_df.empty:
                        fig2 = charts.quick_pie(pie_df, cat2, "count", f"{cat2} Distribution")
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                elif len(numeric_cols) > 1:
                    num2    = numeric_cols[1]
                    hist_sql = f"SELECT \"{num2}\" FROM {dash_table} WHERE \"{num2}\" IS NOT NULL LIMIT 5000"
                    hist_df, _ = db.execute(hist_sql)
                    if hist_df is not None and not hist_df.empty:
                        import plotly.express as px
                        fig3 = px.histogram(hist_df, x=num2, title=f"{num2} Distribution",
                                            template="plotly_dark",
                                            color_discrete_sequence=[THEME["accent2"]])
                        fig3.update_layout(paper_bgcolor=THEME["panel"], plot_bgcolor=THEME["bg"],
                                           font=dict(color=THEME["text"]))
                        st.plotly_chart(fig3, use_container_width=True)

        # Numeric stats table
        if numeric_cols:
            section_header("Numeric Summary", "🔢")
            num_sql = f"SELECT {', '.join([f'ROUND(AVG(\"{c}\"),2) AS avg_{c}, ROUND(MIN(\"{c}\"),2) AS min_{c}, ROUND(MAX(\"{c}\"),2) AS max_{c}' for c in numeric_cols[:6]])} FROM {dash_table}"
            num_df, _ = db.execute(num_sql)
            if num_df is not None:
                st.dataframe(num_df, use_container_width=True)

        # Full data preview
        section_header("Data Preview", "📋")
        prev_sql = f"SELECT * FROM {dash_table} LIMIT 50"
        prev_df, _ = db.execute(prev_sql)
        if prev_df is not None:
            st.dataframe(prev_df, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — REPORT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_report:
    section_header("Generate Report", "📄")

    if not st.session_state["sql_history"] and not st.session_state["profiles"]:
        info_box("Run some queries in the Chat tab first, then generate a report here.")
    else:
        col_l, col_r = st.columns([2, 1])

        with col_r:
            report_title = st.text_input("Report Title", "Data Analysis Report")
            include_sql  = st.checkbox("Include SQL History", value=True)
            include_prof = st.checkbox("Include Data Profile", value=True)

            st.markdown("---")

            if st.button("📝 Generate Markdown Report", use_container_width=True):
                prof_text = ""
                if include_prof and st.session_state["profiles"]:
                    for tbl, prof in st.session_state["profiles"].items():
                        prof_text += profiler.profile_to_text(prof) + "\n\n"

                summary = st.session_state["exec_summary"].get(
                    list(db.tables.keys())[0] if db.tables else "",
                    "No executive summary generated yet."
                )

                md = reporter.generate_markdown(
                    title        = report_title,
                    summary      = summary,
                    findings     = "",
                    sql_history  = st.session_state["sql_history"] if include_sql else [],
                    profile_text = prof_text,
                )
                st.session_state["report_md"] = md

        with col_l:
            if "report_md" in st.session_state:
                section_header("Report Preview", "👁️")
                with st.expander("Preview", expanded=True):
                    st.markdown(st.session_state["report_md"])

                st.download_button(
                    "⬇️ Download Markdown Report",
                    data        = st.session_state["report_md"],
                    file_name   = f"{report_title.replace(' ','_')}.md",
                    mime        = "text/markdown",
                    use_container_width=True,
                )
            else:
                st.markdown(f"""
                <div style='text-align:center;padding:60px;color:{THEME["muted"]}'>
                    <div style='font-size:3rem'>📄</div>
                    <div style='margin-top:12px;font-size:.9rem;color:{THEME["text"]}'>
                        Configure and generate your report
                    </div>
                    <div style='font-size:.8rem;margin-top:6px'>
                        Includes executive summary, SQL history, and data profiles
                    </div>
                </div>
                """, unsafe_allow_html=True)
