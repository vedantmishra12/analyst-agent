"""Senior Data Analyst Agent — orchestrates LLM, SQL, results, and insights."""

import re
import pandas as pd
from services.ollama_service import OllamaService
from database.db_service import DatabaseService

SYSTEM_PROMPT = """You are a Senior Data Analyst and Business Intelligence Expert.
Your role:
- Analyze business data and provide executive-level insights
- Think like a senior analyst: identify risks, opportunities, and trends
- Communicate in clear business language, avoiding excessive technical jargon
- Always be specific with numbers, percentages, and comparisons
- Structure every response as: Executive Summary → Key Findings → Risks → Opportunities → Recommendations

SQL Rules:
- Only generate SELECT queries
- Never use DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE
- Always use proper aliases for readability
- Limit results to reasonable sizes (use LIMIT)

Output Format:
When asked a data question:
1. Write the SQL query wrapped in ```sql ... ```
2. After results are shown, provide business insights
3. Always conclude with 1-2 actionable recommendations
"""

class AnalystAgent:
    def __init__(self, ollama: OllamaService, db: DatabaseService):
        self.ollama = ollama
        self.db     = db

    # ── SQL Generation ──────────────────────────────────────────────────────
    def generate_sql(self, question: str, model: str) -> str:
        schema = self.db.get_schema_prompt()
        prompt = f"""Given this database schema:
{schema}

Generate a DuckDB SQL SELECT query to answer:
"{question}"

Rules:
- Only SELECT queries
- Use LIMIT 500 maximum
- Use proper column aliases
- Handle NULL values appropriately
- Return ONLY the SQL query, no explanation, wrapped in ```sql ... ```
"""
        response = self.ollama.generate(prompt, model, system=SYSTEM_PROMPT)
        return self._extract_sql(response)

    def _extract_sql(self, text: str) -> str:
        patterns = [
            r"```sql\s*(.*?)```",
            r"```\s*(SELECT.*?)```",
            r"(SELECT\s+.*?;)",
        ]
        for pat in patterns:
            match = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        # fallback: find SELECT anywhere
        lines = text.split("\n")
        sql_lines = []
        capturing = False
        for line in lines:
            if line.strip().upper().startswith("SELECT"):
                capturing = True
            if capturing:
                sql_lines.append(line)
                if line.strip().endswith(";"):
                    break
        return " ".join(sql_lines).strip() if sql_lines else ""

    # ── Analysis ────────────────────────────────────────────────────────────
    def analyze_results(self, question: str, sql: str, df: pd.DataFrame, model: str) -> str:
        schema  = self.db.get_schema_prompt()
        preview = df.head(20).to_string(index=False) if not df.empty else "No results."
        stats   = df.describe(include="all").to_string() if not df.empty else ""

        prompt = f"""Schema:
{schema}

User Question: {question}

SQL Executed:
{sql}

Query Results ({len(df)} rows):
{preview}

Statistical Summary:
{stats}

As a Senior Data Analyst, provide:
1. **Executive Summary** (2-3 sentences, business language)
2. **Key Findings** (bullet points with specific numbers)
3. **Risks** (what concerns should leadership know?)
4. **Opportunities** (what actions could improve performance?)
5. **Recommendations** (2-3 specific next steps)

Be concise, data-driven, and business-focused."""

        return self.ollama.generate(prompt, model, system=SYSTEM_PROMPT)

    # ── Chart Suggestion ────────────────────────────────────────────────────
    def suggest_chart(self, question: str, df: pd.DataFrame, model: str) -> dict:
        cols    = list(df.columns)
        dtypes  = {c: str(df[c].dtype) for c in cols}
        prompt  = f"""Given a DataFrame with columns {cols} and dtypes {dtypes},
answering the question: "{question}"

Suggest the best Plotly chart. Respond ONLY in JSON:
{{
  "chart_type": "bar|line|scatter|pie|histogram|treemap|box",
  "x": "column_name_or_null",
  "y": "column_name_or_null",
  "color": "column_name_or_null",
  "title": "chart title"
}}"""
        resp = self.ollama.generate(prompt, model)
        return self._parse_json(resp)

    def _parse_json(self, text: str) -> dict:
        import json
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {}

    # ── KPI Generation ──────────────────────────────────────────────────────
    def generate_kpis(self, model: str) -> str:
        schema = self.db.get_schema_prompt()
        prompt = f"""Given this data schema:
{schema}

Suggest 6 critical KPIs for a business dashboard.
For each KPI, provide the SQL query to calculate it.
Format each as:
KPI Name: <name>
SQL: ```sql <query> ```
"""
        return self.ollama.generate(prompt, model, system=SYSTEM_PROMPT)

    # ── Executive Summary ───────────────────────────────────────────────────
    def generate_executive_summary(self, profile_text: str, model: str) -> str:
        prompt = f"""As a Senior Data Analyst, review this dataset profile and generate an executive summary:

{profile_text}

Provide:
1. **Data Overview** — what is this dataset about?
2. **Data Quality Assessment** — completeness, concerns
3. **Key Observations** — 3-5 most important findings
4. **Recommended Analyses** — what questions should leadership ask?
5. **Data Readiness Score** — rate 1-10 with justification
"""
        return self.ollama.generate(prompt, model, system=SYSTEM_PROMPT)
