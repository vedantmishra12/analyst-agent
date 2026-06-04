"""Global configuration for AI Data Analyst."""
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

SUPPORTED_MODELS = ["llama3", "mistral", "phi3", "llama3.1", "gemma2"]

SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".parquet"]

BLOCKED_SQL_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER",
    "TRUNCATE", "CREATE", "REPLACE", "MERGE", "EXEC",
    "EXECUTE", "GRANT", "REVOKE",
]

MAX_ROWS_DISPLAY = 500
MAX_CHART_ROWS   = 10_000

CHART_COLORS = [
    "#00d4ff", "#7c3aed", "#10b981", "#f59e0b",
    "#ef4444", "#ec4899", "#06b6d4", "#84cc16",
]

THEME = {
    "bg":        "#0a0e1a",
    "panel":     "#111827",
    "border":    "#1e293b",
    "accent":    "#00d4ff",
    "accent2":   "#7c3aed",
    "accent3":   "#10b981",
    "warn":      "#f59e0b",
    "danger":    "#ef4444",
    "text":      "#e2e8f0",
    "muted":     "#64748b",
}
